#!/bin/bash
set -e

echo "🚀 Exabeam MCP Server Setup Script"
echo "=================================="

if [ ! -f ".env.example" ]; then
    echo "❌ Error: .env.example not found. Please run this script from the standalone-mcp-server directory."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "📋 Step 1: Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "📋 Step 1: .env file already exists, skipping..."
fi

echo ""
echo "🔐 Step 2: Generating JWT secret..."

if command -v openssl >/dev/null 2>&1; then
    JWT_SECRET=$(openssl rand -base64 32)
    echo "✅ Generated JWT Secret using OpenSSL: $JWT_SECRET"
elif command -v python3 >/dev/null 2>&1; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ Generated JWT Secret using Python: $JWT_SECRET"
    else
        JWT_SECRET="ExabeamMCP-$(date +%s)-$(whoami)-$(head -c 16 /dev/urandom | base64 | tr -d '=' | tr '+/' '-_')"
        echo "✅ Generated JWT Secret using fallback method: $JWT_SECRET"
    fi
elif command -v node >/dev/null 2>&1; then
    JWT_SECRET=$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ Generated JWT Secret using Node.js: $JWT_SECRET"
    else
        JWT_SECRET="ExabeamMCP-$(date +%s)-$(whoami)-$(head -c 16 /dev/urandom | base64 | tr -d '=' | tr '+/' '-_')"
        echo "✅ Generated JWT Secret using fallback method: $JWT_SECRET"
    fi
else
    JWT_SECRET="ExabeamMCP-$(date +%s)-$(whoami)-$(head -c 16 /dev/urandom | base64 | tr -d '=' | tr '+/' '-_')"
    echo "✅ Generated JWT Secret using fallback method: $JWT_SECRET"
fi

echo ""
echo "💡 Security Note: This secret is unique to your installation."
echo "   Keep it secure and never share it publicly!"

echo ""
echo "⚙️  Step 3: Updating .env file with JWT secret..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/JWT_SECRET=your-super-secure-jwt-secret-key-here/JWT_SECRET=$JWT_SECRET/" .env
else
    sed -i "s/JWT_SECRET=your-super-secure-jwt-secret-key-here/JWT_SECRET=$JWT_SECRET/" .env
fi
echo "✅ Updated .env file with JWT secret"

echo ""
echo "🔑 Step 4: Please update your Exabeam credentials in .env file:"
echo "   - EXABEAM_CLIENT_ID=your-exabeam-client-id"
echo "   - EXABEAM_CLIENT_SECRET=your-exabeam-client-secret"
echo ""
read -p "Press Enter after you've updated the Exabeam credentials in .env file..."

echo ""
echo "🎫 Step 5: Generating test JWT token..."
python3 scripts/generate_token.py generate "$JWT_SECRET" "test-user" "Test User" true 24 > /tmp/jwt_token.txt 2>&1

if [ $? -eq 0 ]; then
    echo "✅ JWT token generated successfully!"
    echo ""
    echo "📋 Your test JWT token:"
    grep "Token:" /tmp/jwt_token.txt | cut -d' ' -f2
    echo ""
    echo "💾 Full token details saved to: /tmp/jwt_token.txt"
else
    echo "❌ Error generating JWT token. Please check the output above."
    cat /tmp/jwt_token.txt
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Review your .env file: cat .env"
echo "2. Start the server: docker-compose up -d"
echo "3. Test the deployment: python scripts/test_connection.py http://localhost:8080 \"$JWT_SECRET\""
echo ""
echo "Your JWT secret: $JWT_SECRET"
echo "Keep this secret secure and use it for generating tokens!"

rm -f /tmp/jwt_token.txt
