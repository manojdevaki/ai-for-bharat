# Sookshma AI - Requirements

**Tagline**: WhatsApp-based AI-powered regulatory intelligence system that reveals how the world regulates what India consumes.

**Hackathon Category**: AI for Retail, Commerce & Market Intelligence

## 1. The Problem

Indian consumers face a critical information gap in retail food markets. While packaged food labels list ingredients, there's no accessible way to understand why certain ingredients are banned or restricted in other regions but allowed in India. This creates information asymmetry in the marketplace, preventing informed purchasing decisions.

The retail intelligence gap is significant: consumers must manually research across multiple regulatory databases to understand ingredient safety profiles. This is impractical for everyday shopping decisions, leaving consumers dependent on brand trust alone. The market lacks a consumer-facing intelligence layer that bridges regulatory knowledge across jurisdictions.

## 2. The User

**Primary Users:**
- Health-conscious consumers in urban India who want to understand what they're consuming
- Parents making food choices for their families
- Individuals with dietary restrictions or health conditions who need ingredient transparency

**Secondary Users:**
- Small food businesses wanting to understand regulatory landscapes for product development
- Food bloggers and influencers creating content about food safety and regulations

**Why WhatsApp:**
WhatsApp is the dominant messaging platform in India with over 400 million users. It provides a familiar, low-friction interface that requires no app downloads or account creation. The image-sharing capability makes it natural for users to photograph food labels, and the conversational format allows for follow-up questions and clarifications.

## 3. The AI Edge

**This solution is fundamentally AI-native and cannot exist without it:**

**Unstructured Data Intelligence:** Food labels in Indian retail are chaotic—curved packaging, mixed Hindi-English text, varying fonts, poor lighting, and inconsistent layouts. Traditional OCR achieves ~60% accuracy on real-world labels. AI-powered vision models handle these variations, extracting structured data from unstructured retail imagery at scale.

**Entity Resolution at Scale:** A single ingredient appears as "Sunset Yellow FCF," "E110," "FD&C Yellow No. 6," "CI 15985," or "खाद्य रंग पीला" across different markets. Rule-based matching fails catastrophically with thousands of ingredient variations. AI performs semantic entity resolution, understanding that these are the same substance despite different naming conventions.

**Cross-Jurisdictional Market Intelligence:** Understanding regulatory differences requires reasoning over complex, evolving regulatory texts from FSSAI, EFSA, and FDA. AI synthesizes information from multiple authoritative sources, identifies contradictions, and generates evidence-based explanations. This is market intelligence generation, not database lookup.

**Conversational Commerce Interface:** Users ask follow-up questions like "Is this safe for children?" or "Why is this banned in Europe?" AI maintains context, interprets intent, and provides relevant answers without requiring structured queries. This transforms regulatory data into accessible consumer intelligence.

**Why This Is AI for Market Intelligence:** The system doesn't just retrieve data—it performs real-time analysis of retail products, normalizes cross-market information, and generates actionable intelligence for consumer decision-making. This is AI-powered market transparency at the point of purchase.

## 4. The Success Metric

**For MVP Success:**
- Successfully extract and identify ingredients from 80% of clear food label images
- Provide accurate regulatory status comparison for at least 100 common food ingredients across India, EU, and US
- Generate coherent explanations for regulatory differences in under 10 seconds
- Handle 50+ demo interactions during hackathon presentation without system failures

**Observable Indicators:**
- Users can photograph a food label and receive a meaningful response
- System correctly identifies when ingredients have different regulatory status across regions
- Explanations are factual, source-grounded, and avoid medical advice
- Demo showcases real-world food products with actual regulatory differences

## 5. The Features

**Core MVP Features:**

1. **Image Processing**: Accept food label images via WhatsApp and extract ingredient lists using AI-powered OCR
2. **Ingredient Recognition**: Identify and normalize ingredient names to standard regulatory terminology using semantic understanding
3. **Regulatory Comparison**: Compare ingredient status across India (FSSAI), EU, and US regulatory frameworks
4. **Explanation Generation**: Provide clear, factual explanations for why ingredients have different regulatory status
5. **WhatsApp Integration**: Seamless conversation flow with image upload and text responses
6. **Error Handling**: Graceful handling of unclear images, unrecognized ingredients, or system limitations

**Responsible Design & Limitations:**

- **Informational Only**: System provides regulatory facts, not medical advice, dietary recommendations, or legal guidance
- **Source Transparency**: All regulatory comparisons are grounded in public FSSAI, EU, and US regulatory databases
- **Clear Disclaimers**: Users are informed that regulatory status does not equal safety recommendations
- **Scope Boundaries**: MVP focuses exclusively on packaged food products; cosmetics and personal care are out of scope
- **Data Currency**: System acknowledges that regulatory data is current as of a specific date and may change
- **No Health Claims**: System avoids language that could be interpreted as health or safety advice

**Future Extensions:**
- Cosmetics and personal care products
- Web application and mobile apps for broader accessibility
- Additional regulatory regions (Canada, Australia, Japan)
- Nutritional analysis integration
- Allergen detection and warnings