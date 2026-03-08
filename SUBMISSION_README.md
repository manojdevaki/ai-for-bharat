# Sookshma AI - AWS AI for Bharat Hackathon Submission

![Sookshma AI Logo](docs/sookshma-ai-logo.png)

**Live Demo:** https://sookshma.ai.manojdevaki.com

---

## 🎯 Project Overview

**Sookshma AI** is an AI-powered regulatory intelligence system that helps Indian consumers understand food ingredient regulations across India (FSSAI), European Union (EFSA), and United States (FDA). Simply upload a food label photo and get instant, jurisdiction-specific regulatory analysis.

### Problem Statement

Millions of Indian consumers read food labels daily but lack instant access to:
- Regulatory approval status across jurisdictions
- Health-impact context of regulated additives
- Transparent data about ingredient safety differences between countries

### Solution

Sookshma AI provides point-of-purchase regulatory intelligence by:
- **OCR extraction** using Amazon Textract
- **AI-powered analysis** using Amazon Bedrock (Meta Llama 3)
- **Source-locked regulatory database** with explicit data-gap flagging
- **Responsible AI** with non-medical, informational explanations

---

## 🏗️ Architecture

### AWS Services Used

- **Amazon Textract** - Intelligent OCR for ingredient extraction
- **Amazon Bedrock** - Meta Llama 3 8B for regulatory explanations
- **AWS Lambda** - Serverless compute for all handlers
- **Amazon DynamoDB** - NoSQL database for regulatory data and sessions
- **Amazon S3** - Image storage and static website hosting
- **Amazon API Gateway** - RESTful API endpoints
- **Amazon CloudFront** - CDN for global distribution
- **AWS Certificate Manager** - SSL/TLS certificates
- **Amazon Route 53** - DNS management

### System Flow

```
User uploads image → Textract OCR → Ingredient extraction → 
DynamoDB lookup → Bedrock AI explanation → Response with 
regulated vs non-regulated ingredients
```

---

## 🚀 Key Features

### 1. Intelligent Ingredient Extraction
- Textract-powered OCR with high accuracy
- E-number detection and normalization
- Handles various label formats and languages

### 2. Multi-Jurisdiction Analysis
- **India (FSSAI)** - Food Safety and Standards Authority
- **EU (EFSA)** - European Food Safety Authority  
- **US (FDA)** - Food and Drug Administration

### 3. Responsible AI
- Non-medical, informational explanations only
- Clear disclaimers on every response
- Source-backed regulatory statuses with authority citations
- Explicit "not_listed" status for missing FDA data (no guessing)

### 4. Source-Locked Data Quality
- Strict validation: only ingredients with verified sources for all 3 jurisdictions
- Transparent data gaps rather than placeholder values
- Regulatory health-impact context without medical claims

### 5. Clean User Experience
- Upload via drag-drop, file picker, or camera
- Clear separation of regulated vs non-regulated ingredients
- Detailed explanations for each regulated additive
- "Analyze Another Image" button for seamless workflow

---

## 📁 Project Structure

```
Bharat-Submission/
├── src/                          # Lambda function code
│   ├── handlers/                 # API handlers
│   │   ├── web/                  # Web API handler
│   │   ├── webhook/              # WhatsApp webhook (in progress)
│   │   └── static/               # Static file handler
│   ├── services/                 # Business logic
│   │   ├── ingredient/           # Ingredient processing
│   │   ├── regulatory/           # Regulatory analysis
│   │   └── whatsapp/             # WhatsApp client
│   └── utils/                    # Utilities
│       ├── bedrock/              # Bedrock AI client
│       └── dynamodb/             # DynamoDB client
├── web/                          # Frontend web interface
│   ├── index.html                # Main UI
│   └── sookshma-ai-logo.png      # Logo
├── scripts/                      # Data management scripts
│   ├── fetch_real_regulatory_data.py
│   ├── build_source_locked_dataset.py
│   ├── load_regulatory_data.py
│   └── deploy.sh                 # Deployment script
├── data/regulatory/              # Regulatory datasets
│   ├── official_ingredients.json
│   └── source_locked_ingredients.json
├── tests/                        # Unit tests
├── docs/                         # Documentation
├── template.yaml                 # AWS SAM template
├── DEMO_VIDEO_SCRIPT.md          # Demo video script
└── SUBMISSION_README.md          # This file
```

---

## 🛠️ Setup & Deployment

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.13
- Node.js (for frontend testing)

### Environment Variables Required

```bash
WHATSAPP_PHONE_NUMBER_ID=<your-whatsapp-phone-id>
WHATSAPP_ACCESS_TOKEN=<your-whatsapp-token>
WHATSAPP_VERIFY_TOKEN=<your-verify-token>
```

### Deployment Steps

1. **Clone and setup:**
```bash
cd Bharat-Submission
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r src/requirements.txt
```

2. **Load regulatory data:**
```bash
python scripts/load_regulatory_data.py
```

3. **Deploy infrastructure:**
```bash
bash scripts/deploy.sh
```

4. **Upload web files to S3:**
```bash
aws s3 sync web/ s3://sookshma-ai-website/ --cache-control "max-age=300"
```

### Testing Locally

```bash
# Run unit tests
python -m pytest tests/

# Test ingredient processor
python -c "from src.services.ingredient.processor import IngredientProcessor; print(IngredientProcessor().extract_ingredients_from_text('Water, E211, Sugar'))"
```

---

## 📊 Data Sources

### Official Regulatory Sources

1. **FSSAI (India)**
   - Food Safety and Standards (Food Product Standards and Food Additives) Regulations, 2011
   - Official compendium of food additives

2. **EU (European Union)**
   - Regulation (EC) No 1333/2008
   - EU Food Additives Database

3. **FDA (United States)**
   - Code of Federal Regulations (CFR) Title 21
   - GRAS (Generally Recognized as Safe) list
   - Explicit "not_listed" for missing entries

### Data Quality Measures

- **Source-locked dataset:** Only ingredients with verified sources for all 3 jurisdictions
- **Rejected ingredients list:** Tracks ingredients with incomplete data
- **Authority citations:** Every status includes regulatory authority reference
- **Transparent gaps:** "not_listed" status instead of guessing

---

## 🎥 Demo Video

See `DEMO_VIDEO_SCRIPT.md` for complete recording script including:
- Problem statement and solution overview
- Live demo walkthrough
- Technical architecture explanation
- Responsible AI approach
- Future vision (skincare products, WhatsApp integration)

**Demo URL:** https://sookshma.ai.manojdevaki.com

---

## 🔮 Future Roadmap

### Skincare & Cosmetics Expansion
- **Why:** Cosmetics have 1000+ regulated ingredients vs 100s in food
- **Complexity:** More jurisdictional variance, allergen tracking, concentration limits
- **Use case:** "Is this face cream safe? Does it contain parabens banned in EU?"
- **Data sources:** EU CosIng database, FDA cosmetics list, CDSCO India

### WhatsApp Integration (In Progress)
- **Status:** Conversational interface under development
- **Value:** Mobile-first experience for Indian market
- **Flow:** Send photo → Get instant analysis → Ask follow-up questions

### Additional Enhancements
- Barcode scanning for instant product lookup
- Allergen cross-reference and personalized alerts
- Historical regulatory change tracking
- Multi-language support (Hindi, Tamil, Telugu, etc.)

---

## 🧪 Testing

### Test Coverage

- Unit tests for ingredient processor
- Unit tests for regulatory analyzer
- Unit tests for Bedrock client
- Integration tests for complete flow

### Sample Test Images

Located in `tests/` directory:
- `Ching-s-Secret-Green-Chilli-Sauce-Bold-And-Flavourful.webp`

---

## 📝 API Documentation

### POST /api/analyze

**Request:**
```json
{
  "image": "<base64-encoded-image>"
}
```

**Response:**
```json
{
  "regulated_ingredients": [
    {
      "name": "Acetic Acid",
      "e_number": "E260",
      "original_ingredient": "Acidity Regulator (E260)",
      "jurisdictions": {
        "india": {"status": "approved", "authority": "FSSAI"},
        "eu": {"status": "approved", "authority": "EFSA"},
        "us": {"status": "gras", "authority": "FDA"}
      },
      "explanation": "AI-generated regulatory explanation..."
    }
  ],
  "non_regulated_ingredients": [
    {"name": "Water", "normalized": "water"},
    {"name": "Sugar", "normalized": "sugar"}
  ],
  "total_ingredients_found": 8,
  "regulated_count": 3,
  "non_regulated_count": 5
}
```

---

## 🏆 Hackathon Highlights

### Innovation
- First-of-its-kind multi-jurisdiction regulatory intelligence for Indian consumers
- Source-locked data quality with transparent gap flagging
- Responsible AI with non-medical explanations

### AWS AI Services
- Amazon Textract for intelligent OCR
- Amazon Bedrock with Meta Llama 3 for natural language generation
- Serverless architecture for scalability

### Impact
- Empowers informed consumer choice at point of purchase
- Bridges regulatory knowledge gap between jurisdictions
- Scalable to skincare/cosmetics (future expansion)

### Technical Excellence
- Clean separation of concerns (handlers, services, utils)
- Comprehensive error handling and logging
- Unit test coverage
- Production-ready deployment

---

## 👥 Team

**Developer:** Manoj Sainadh Devaki  
**GitHub:** https://github.com/manojdevaki/sookshma-ai  
**Live Demo:** https://sookshma.ai.manojdevaki.com

---

## 📄 License

This project is submitted for the AWS AI for Bharat Hackathon.

---

## 🙏 Acknowledgments

- AWS AI for Bharat Hackathon organizers
- Amazon Bedrock team for Meta Llama 3 access
- FSSAI, EFSA, and FDA for public regulatory data
- Open source community for tools and libraries

---

**Built with ❤️ for the AWS AI for Bharat Hackathon**
