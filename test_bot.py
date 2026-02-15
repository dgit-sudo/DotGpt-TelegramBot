"""
Basic tests for the E-commerce Telegram Bot
"""
import os
import sys
import unittest
from datetime import datetime

# Set test environment
os.environ['DATABASE_URL'] = 'sqlite:///test_bot_database.db'
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['ADMIN_USER_ID'] = '123456789'

from models import init_db, get_session, User, Product, Chat, Message
from translations import get_text, TRANSLATIONS


class TestModels(unittest.TestCase):
    """Test database models"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.engine = init_db('sqlite:///:memory:')
    
    def setUp(self):
        """Create a new session for each test"""
        self.session = get_session(self.engine)
    
    def tearDown(self):
        """Clean up session"""
        self.session.close()
    
    def test_create_user(self):
        """Test creating a user"""
        user = User(
            telegram_id=12345,
            username='testuser',
            first_name='Test',
            last_name='User',
            role='buyer'
        )
        self.session.add(user)
        self.session.commit()
        
        retrieved_user = self.session.query(User).filter_by(telegram_id=12345).first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, 'testuser')
        self.assertEqual(retrieved_user.role, 'buyer')
    
    def test_create_product(self):
        """Test creating a product"""
        # First create a supplier
        supplier = User(
            telegram_id=54321,
            username='supplier',
            first_name='Supplier',
            role='supplier'
        )
        self.session.add(supplier)
        self.session.commit()
        
        # Create product
        product = Product(
            name='Test Product',
            description='A test product',
            price=99.99,
            currency='USD',
            supplier_id=supplier.id,
            payment_methods='Credit Card, PayPal'
        )
        self.session.add(product)
        self.session.commit()
        
        retrieved_product = self.session.query(Product).filter_by(name='Test Product').first()
        self.assertIsNotNone(retrieved_product)
        self.assertEqual(retrieved_product.price, 99.99)
        self.assertEqual(retrieved_product.supplier_id, supplier.id)
    
    def test_create_chat(self):
        """Test creating a chat"""
        # Create buyer and supplier
        buyer = User(telegram_id=11111, username='buyer', role='buyer')
        supplier = User(telegram_id=22222, username='supplier', role='supplier')
        self.session.add_all([buyer, supplier])
        self.session.commit()
        
        # Create product
        product = Product(
            name='Chat Product',
            price=50.0,
            supplier_id=supplier.id
        )
        self.session.add(product)
        self.session.commit()
        
        # Create chat
        chat = Chat(
            buyer_id=buyer.id,
            supplier_id=supplier.id,
            product_id=product.id
        )
        self.session.add(chat)
        self.session.commit()
        
        retrieved_chat = self.session.query(Chat).first()
        self.assertIsNotNone(retrieved_chat)
        self.assertEqual(retrieved_chat.buyer_id, buyer.id)
        self.assertEqual(retrieved_chat.supplier_id, supplier.id)
    
    def test_create_message(self):
        """Test creating a message"""
        # Create users
        buyer = User(telegram_id=33333, username='buyer2', role='buyer')
        supplier = User(telegram_id=44444, username='supplier2', role='supplier')
        self.session.add_all([buyer, supplier])
        self.session.commit()
        
        # Create chat
        chat = Chat(buyer_id=buyer.id, supplier_id=supplier.id)
        self.session.add(chat)
        self.session.commit()
        
        # Create message
        message = Message(
            chat_id=chat.id,
            sender_id=buyer.id,
            receiver_id=supplier.id,
            message_text='Hello, I am interested in this product'
        )
        self.session.add(message)
        self.session.commit()
        
        retrieved_message = self.session.query(Message).first()
        self.assertIsNotNone(retrieved_message)
        self.assertEqual(retrieved_message.message_text, 'Hello, I am interested in this product')
        self.assertEqual(retrieved_message.sender_id, buyer.id)


class TestTranslations(unittest.TestCase):
    """Test translation functionality"""
    
    def test_all_languages_exist(self):
        """Test that all 6 languages are present"""
        expected_languages = ['en', 'es', 'fr', 'de', 'it', 'pt']
        for lang in expected_languages:
            self.assertIn(lang, TRANSLATIONS)
    
    def test_get_text_english(self):
        """Test getting English text"""
        text = get_text('en', 'welcome')
        self.assertIn('Welcome', text)
        self.assertIn('E-commerce', text)
    
    def test_get_text_spanish(self):
        """Test getting Spanish text"""
        text = get_text('es', 'welcome')
        self.assertIn('Bienvenido', text)
    
    def test_get_text_french(self):
        """Test getting French text"""
        text = get_text('fr', 'welcome')
        self.assertIn('Bienvenue', text)
    
    def test_get_text_german(self):
        """Test getting German text"""
        text = get_text('de', 'welcome')
        self.assertIn('Willkommen', text)
    
    def test_get_text_italian(self):
        """Test getting Italian text"""
        text = get_text('it', 'welcome')
        self.assertIn('Benvenuto', text)
    
    def test_get_text_portuguese(self):
        """Test getting Portuguese text"""
        text = get_text('pt', 'welcome')
        self.assertIn('Bem-vindo', text)
    
    def test_get_text_with_formatting(self):
        """Test getting text with formatting"""
        text = get_text('en', 'product_details',
                       name='Test Product',
                       price=99.99,
                       currency='USD',
                       supplier='John',
                       payment='PayPal',
                       description='Great product')
        self.assertIn('Test Product', text)
        self.assertIn('99.99', text)
        self.assertIn('USD', text)
        self.assertIn('John', text)
    
    def test_get_text_fallback(self):
        """Test fallback to English for unknown language"""
        text = get_text('unknown_lang', 'welcome')
        # Should fallback to English
        self.assertIn('Welcome', text)
    
    def test_all_keys_present(self):
        """Test that all languages have the same keys"""
        english_keys = set(TRANSLATIONS['en'].keys())
        for lang in ['es', 'fr', 'de', 'it', 'pt']:
            lang_keys = set(TRANSLATIONS[lang].keys())
            self.assertEqual(english_keys, lang_keys,
                           f"Language {lang} is missing some keys")


class TestDatabaseRelationships(unittest.TestCase):
    """Test database relationships"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.engine = init_db('sqlite:///:memory:')
    
    def setUp(self):
        """Create a new session for each test"""
        self.session = get_session(self.engine)
    
    def tearDown(self):
        """Clean up session"""
        self.session.close()
    
    def test_user_product_relationship(self):
        """Test user to products relationship"""
        supplier = User(telegram_id=99999, username='supplier3', role='supplier')
        self.session.add(supplier)
        self.session.commit()
        
        product1 = Product(name='Product 1', price=10.0, supplier_id=supplier.id)
        product2 = Product(name='Product 2', price=20.0, supplier_id=supplier.id)
        self.session.add_all([product1, product2])
        self.session.commit()
        
        retrieved_supplier = self.session.query(User).filter_by(telegram_id=99999).first()
        self.assertEqual(len(retrieved_supplier.products), 2)
        self.assertIn('Product 1', [p.name for p in retrieved_supplier.products])
        self.assertIn('Product 2', [p.name for p in retrieved_supplier.products])
    
    def test_chat_messages_relationship(self):
        """Test chat to messages relationship"""
        buyer = User(telegram_id=55555, username='buyer3', role='buyer')
        supplier = User(telegram_id=66666, username='supplier4', role='supplier')
        self.session.add_all([buyer, supplier])
        self.session.commit()
        
        chat = Chat(buyer_id=buyer.id, supplier_id=supplier.id)
        self.session.add(chat)
        self.session.commit()
        
        msg1 = Message(chat_id=chat.id, sender_id=buyer.id, receiver_id=supplier.id, message_text='Message 1')
        msg2 = Message(chat_id=chat.id, sender_id=supplier.id, receiver_id=buyer.id, message_text='Message 2')
        self.session.add_all([msg1, msg2])
        self.session.commit()
        
        retrieved_chat = self.session.query(Chat).first()
        self.assertEqual(len(retrieved_chat.messages), 2)


if __name__ == '__main__':
    # Clean up test database if it exists
    if os.path.exists('test_bot_database.db'):
        os.remove('test_bot_database.db')
    
    # Run tests
    unittest.main()
