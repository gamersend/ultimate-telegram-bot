#!/bin/bash
# Test Bot Configuration

echo "🧪 Testing Bot Configuration..."

# Test Python imports
python3 -c "
try:
    import bot.main
    print('✅ Bot imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)

try:
    from bot.config import settings
    print('✅ Configuration loaded')
    
    if settings.telegram_bot_token:
        print('✅ Telegram token configured')
    else:
        print('⚠️ Telegram token not configured')
        
    if settings.openai_api_key:
        print('✅ OpenAI API key configured')
    else:
        print('⚠️ OpenAI API key not configured')
        
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

echo "🎉 Test complete!"
