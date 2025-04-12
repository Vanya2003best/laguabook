# app/services/ai_service.py
import logging
from flask import current_app
from openai import OpenAI
from ..models import db, WordInfo, ChatHistory
from datetime import datetime

logger = logging.getLogger(__name__)


# app/services/ai_service.py
class AIService:
    """Service for interacting with OpenAI API"""

    def __init__(self):
        """Initialize the OpenAI client"""
        self.client = None
        self.model = None

    def _ensure_client(self):
        """Ensure the OpenAI client is initialized"""
        if not self.client:
            from flask import current_app
            try:
                self.client = OpenAI(
                    api_key=current_app.config['OPENAI_API_KEY'],
                    organization=current_app.config.get('OPENAI_ORG_ID'),
                    project=current_app.config.get('OPENAI_PROJECT_ID')
                )
                self.model = current_app.config.get('OPENAI_MODEL', 'gpt-4o-mini')
            except Exception as e:
                current_app.logger.error(f"Error initializing OpenAI client: {e}")
                raise

    def get_word_info(self, word, source_language, target_language, user_id=None, session_id=None):
        """Get information about a word

        Args:
            word: The word to look up
            source_language: The language of the word
            target_language: The language to explain in
            user_id: Optional user ID for tracking history
            session_id: Optional session ID for tracking history

        Returns:
            Dictionary with word information
        """
        self._ensure_client()  # Инициализируем клиента, только когда он нужен
        # Check if word info exists in cache
        cached_info = WordInfo.query.filter_by(word=word, language=source_language).first()

        if cached_info:
            # Update access stats
            cached_info.last_accessed = datetime.utcnow()
            cached_info.access_count += 1
            db.session.commit()
            return {
                'info': cached_info.info,
                'examples': cached_info.examples,
                'cached': True
            }

        # If not in cache, query the API
        try:
            # Create prompt based on language
            prompt = self._create_word_info_prompt(word, source_language, target_language)

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt['system']},
                    {"role": "user", "content": prompt['user']}
                ]
            )

            response_text = completion.choices[0].message.content

            # Save word info to database
            word_info = WordInfo(
                word=word,
                language=source_language,
                info=response_text,
                examples=None  # Could extract examples from response in the future
            )
            db.session.add(word_info)

            # Save chat history if user_id is provided
            if user_id and session_id:
                system_message = ChatHistory(
                    user_id=user_id,
                    session_id=session_id,
                    role='system',
                    content=prompt['system'],
                    word=word
                )
                user_message = ChatHistory(
                    user_id=user_id,
                    session_id=session_id,
                    role='user',
                    content=prompt['user'],
                    word=word
                )
                assistant_message = ChatHistory(
                    user_id=user_id,
                    session_id=session_id,
                    role='assistant',
                    content=response_text,
                    word=word
                )
                db.session.add_all([system_message, user_message, assistant_message])

            db.session.commit()

            return {
                'info': response_text,
                'examples': None,
                'cached': False
            }

        except Exception as e:
            logger.error(f"Error querying OpenAI API for word '{word}': {e}")
            db.session.rollback()
            return {
                'info': f"Error retrieving information for '{word}'. Please try again later.",
                'examples': None,
                'error': str(e),
                'cached': False
            }

    def send_chat_message(self, message, chat_history, user_id=None, session_id=None):
        """
        Send a message to the chat API

        Args:
            message: The user's message
            chat_history: List of previous messages
            user_id: Optional user ID for tracking history
            session_id: Optional session ID for tracking history

        Returns:
            Response text from the API
        """
        try:
            messages = [{"role": m["role"], "content": m["content"]} for m in chat_history]
            messages.append({"role": "user", "content": message})

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            response_text = completion.choices[0].message.content

            # Save chat history if user_id is provided
            if user_id and session_id:
                user_message = ChatHistory(
                    user_id=user_id,
                    session_id=session_id,
                    role='user',
                    content=message
                )
                assistant_message = ChatHistory(
                    user_id=user_id,
                    session_id=session_id,
                    role='assistant',
                    content=response_text
                )
                db.session.add_all([user_message, assistant_message])
                db.session.commit()

            return {
                'response': response_text,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error sending chat message: {e}")
            return {
                'response': "Sorry, I'm having trouble connecting to the language assistant. Please try again later.",
                'error': str(e)
            }

    def _create_word_info_prompt(self, word, source_language, target_language):
        """Create appropriate prompt based on languages"""
        language_codes = {
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pl': 'Polish',
            'ru': 'Russian'
        }

        source_lang_name = language_codes.get(source_language, source_language)
        target_lang_name = language_codes.get(target_language, target_language)

        system_prompt = f"You are a helpful language learning assistant. You provide clear, concise information about {source_lang_name} words in {target_lang_name}."

        user_prompt = f"""Please provide the following information about the {source_lang_name} word '{word}' in {target_lang_name}:

1. Basic form and part of speech
2. Grammar rule or pattern that applies to this word (to help with memorization)
3. Common forms of this word (conjugations, declensions, etc. if applicable)
4. Two example sentences showing common usage
5. Any useful notes for language learners (cognates, common pitfalls, etc.)

Format your response in a clear, structured way that would be helpful for a language learner."""

        return {
            'system': system_prompt,
            'user': user_prompt
        }