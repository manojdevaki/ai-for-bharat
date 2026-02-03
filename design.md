# Sookshma AI - Design

## 1. High-Level Architecture

The system operates as a serverless, event-driven architecture on AWS, delivering real-time market intelligence through a conversational interface. Users interact through WhatsApp Business Cloud API, which triggers webhook events to API Gateway. Lambda functions orchestrate the AI workflow: image processing through Textract, ingredient extraction and regulatory reasoning through Bedrock, and intelligent data retrieval from DynamoDB and OpenSearch. The system transforms unstructured retail product data into structured market intelligence while maintaining regulatory data in optimized storage for fast retrieval.

## 2. Major Components

**WhatsApp Interface**: Handles incoming messages, image uploads, and outbound responses through WhatsApp Business Cloud API webhooks.

**Backend Orchestration**: Lambda functions manage the workflow, coordinate between services, handle state management, and ensure proper error handling and user feedback.

**OCR Service**: Amazon Textract extracts text from food label images, handling various image qualities, orientations, and packaging formats.

**AI Reasoning Layer**: Amazon Bedrock with Claude 3 Sonnet processes extracted text, normalizes ingredient names, performs regulatory comparisons, and generates explanations.

**Data Storage**: DynamoDB stores regulatory data and user sessions, while OpenSearch provides vector-based ingredient matching and retrieval augmented generation (RAG) capabilities.

## 3. System & User Flows

1. User sends food label image via WhatsApp
2. WhatsApp Business API receives message and triggers API Gateway webhook
3. Lambda function validates message and extracts image URL
4. Image is downloaded and processed through Amazon Textract for OCR
5. Extracted text is sent to Bedrock (Claude 3 Sonnet) for ingredient identification
6. System queries OpenSearch for regulatory data on identified ingredients
7. Bedrock generates comparative analysis and explanation of regulatory differences
8. Response is formatted and sent back to user via WhatsApp
9. System handles follow-up questions and maintains conversation context

## 4. AWS Integration

**Amazon Bedrock as Core AI Engine:** Bedrock with Claude 3 Sonnet serves as the central reasoning engine due to its strong document understanding, long-context reasoning, and ability to generate clear, source-grounded explanations from complex regulatory texts while maintaining low latency and cost suitable for a chat-based user experience. This is the AI backbone that enables market intelligence generation.

**Amazon Textract for Retail Data Extraction:** Provides robust OCR capabilities for extracting text from food labels regardless of image quality, packaging complexity, or mixed-language content common in Indian retail.

**AWS Lambda for Serverless Orchestration:** Enables serverless execution with automatic scaling, perfect for handling variable WhatsApp message volumes during hackathon demos and real-world usage spikes.

**Amazon DynamoDB for Fast Data Access:** Offers fast, consistent storage for regulatory data and user session management with single-digit millisecond latency, ensuring responsive user experience.

**Amazon OpenSearch for Intelligent Retrieval:** Powers semantic search and RAG functionality across regulatory databases, enabling AI to retrieve relevant regulatory context for accurate comparisons.

**Amazon S3 for Data Persistence:** Stores processed images and regulatory documents for reference, audit trails, and continuous improvement of the AI system.

## 5. Technical Logic

**Ingredient Extraction:** Textract OCR output is processed by Bedrock to identify ingredient lists, handling various formats, languages (English, Hindi), and E-number notations commonly found on Indian food labels. AI distinguishes ingredients from nutritional information, branding, and other label text.

**Normalization:** Claude 3 Sonnet performs semantic entity resolution, mapping ingredient variations (chemical names, E-numbers, common names, regional spellings) to standardized regulatory identifiers. This enables accurate cross-regional comparisons despite naming inconsistencies.

**Regulatory Comparison:** System queries structured regulatory data for India (FSSAI), EU, and US, identifying differences in approval status, usage limits, or restrictions for each ingredient. AI synthesizes this into comparative intelligence.

**Explanation Generation:** Bedrock generates clear, factual explanations that avoid medical advice while explaining the rationale behind different regulatory approaches. Responses are grounded in source documents and include appropriate disclaimers.

**Error Handling:** System gracefully handles unclear images, unrecognized ingredients, or missing regulatory data by providing helpful feedback and suggesting alternative approaches. Users receive clear communication about system limitations.

**Responsible AI Implementation:**
- All responses include disclaimers that information is factual, not medical advice
- System cites regulatory sources for transparency
- Unclear or ambiguous results are flagged rather than guessed
- User queries are not stored beyond session context for privacy

**Future Extensions:** Architecture supports expansion to cosmetics and personal care products through additional regulatory data sources and specialized reasoning prompts. The serverless backend design enables easy integration with web and mobile applications through the same API Gateway endpoints, allowing multi-channel access beyond WhatsApp.