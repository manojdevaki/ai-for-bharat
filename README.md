# 🔍 Sookshma AI - Food Ingredient Intelligence

**AI-powered regulatory intelligence system that reveals how the world regulates what India consumes.**

[![AWS](https://img.shields.io/badge/AWS-Serverless-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Business%20API-green)](https://developers.facebook.com/docs/whatsapp/)

## 🌟 **Live Demo**

- **🌐 Web Interface**: [https://sookshma.ai.manojdevaki.com](https://sookshma.ai.manojdevaki.com)
- **💬 WhatsApp Bot**: [Start Chat](https://wa.me/15550100234?text=Hi!%20I%20want%20to%20analyze%20food%20ingredients.%20Can%20you%20help%20me%3F)

## 🎯 **What It Does**

Sookshma AI bridges the information gap for Indian consumers by providing accessible regulatory intelligence on food ingredients across India, EU, and US markets through familiar interfaces.

### **Key Features**
- 📸 **OCR Analysis**: Extract text from food label images using Amazon Textract
- 🧠 **AI Processing**: Identify and normalize ingredients using Meta Llama 3
- 🌍 **Cross-Jurisdictional**: Compare regulations across India (FSSAI), EU (EFSA), and US (FDA)
- 💬 **WhatsApp Integration**: Conversational interface for real-time analysis
- 🌐 **Web Interface**: Modern web app with camera capture and drag-drop upload

## 🏗️ **Architecture**

**Serverless, Event-Driven Architecture** on AWS:

- **Amazon Bedrock (Meta Llama 3)**: AI reasoning and explanation generation
- **Amazon Textract**: OCR for food label text extraction
- **AWS Lambda**: Serverless orchestration
- **Amazon DynamoDB**: Fast regulatory data storage
- **Amazon API Gateway**: RESTful API and WhatsApp webhook
- **WhatsApp Business API**: Primary user interface

## 🚀 **Quick Start**

### **Prerequisites**
- AWS Account with Bedrock access
- WhatsApp Business Account
- Python 3.13+
- AWS SAM CLI

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/sookshma-ai.git
cd sookshma-ai
```

### **2. Set Environment Variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

### **3. Deploy to AWS**
```bash
./deploy.sh
```

### **4. Load Regulatory Data**
```bash
python scripts/load_regulatory_data.py
```

## 📱 **Usage**

### **Web Interface**
1. Visit [https://sookshma.ai.manojdevaki.com](https://sookshma.ai.manojdevaki.com)
2. Upload or capture a food label image
3. Get instant regulatory analysis

### **WhatsApp**
1. Message: [+1 555 0100 1234](https://wa.me/15550100234?text=Hi!%20I%20want%20to%20analyze%20food%20ingredients.%20Can%20you%20help%20me%3F)
2. Send "Hi! I want to analyze food ingredients"
3. Upload a food label photo
4. Receive AI-powered analysis

## 🧪 **Testing**

```bash
# Run unit tests
python -m pytest tests/

# Test WhatsApp integration
python tests/test_whatsapp_integration.py

# Test regulatory analysis
python tests/test_regulatory_analyzer.py
```

## 📊 **Performance**

- **Response Time**: 3-8 seconds average
- **OCR Accuracy**: 85%+ on clear images
- **Ingredient Coverage**: 107 regulated ingredients
- **Jurisdictions**: 3 (India, EU, US)
- **Uptime**: 99.9% (AWS Lambda)

## 🔒 **Responsible AI**

- **Informational Only**: Provides regulatory facts, not medical advice
- **Source Transparency**: All data from official regulatory databases
- **Clear Disclaimers**: Regulatory status ≠ safety recommendations
- **Privacy First**: No user data storage beyond session context

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 **Hackathon**

Built for the **AWS AI for Bharat Hackathon** in the "AI for Retail, Commerce & Market Intelligence" category.

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/yourusername/sookshma-ai/issues)
- **Documentation**: [docs/](docs/)
- **Email**: devakimanojsainadh@gmail.com

---

**Made with ❤️ for food transparency and consumer empowerment in India** 🇮🇳