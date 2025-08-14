#!/usr/bin/env python3
"""
Generate additional keywords following the established patterns for VQA dataset
"""

# Domain categories
domains = [
    "agriculture", "architecture", "automotive", "banking", "biology", "business", 
    "chemistry", "civics", "climate", "computer science", "construction", "cooking",
    "culture", "design", "economics", "education", "electronics", "energy", 
    "engineering", "environment", "finance", "food safety", "geography", "geology",
    "government", "health", "history", "hospitality", "law", "library", "logistics",
    "manufacturing", "marketing", "mathematics", "media", "medical", "meteorology",
    "music", "news", "nursing", "nutrition", "office", "pharmacy", "physics",
    "policy", "politics", "postal", "public health", "public safety", "railway",
    "retail", "safety", "sanitation", "science", "security", "software", "sports",
    "statistics", "supply chain", "tourism", "traffic", "transportation", 
    "urban planning", "utilities", "veterinary", "warehouse", "workplace",
    "aerospace", "biotechnology", "cybersecurity", "forensics", "robotics",
    "telecommunications", "textiles", "pharmaceuticals", "renewable energy",
    "mining", "agriculture technology", "marine", "aviation", "defense",
    "entertainment", "gaming", "publishing", "broadcasting", "film production",
    "advertising", "consulting", "real estate", "insurance", "investment",
    "nonprofit", "research", "testing", "quality assurance", "compliance"
]

# Document types
doc_types = [
    "ad", "advertisement", "announcement", "application", "banner", "billboard",
    "brochure", "bulletin", "catalog", "certificate", "chart", "checklist",
    "coupon", "curriculum", "diagram", "diploma", "directory", "document",
    "faq", "flyer", "flowchart", "form", "glossary", "graph", "guide",
    "handbook", "instruction", "invoice", "label", "letter", "list",
    "log", "manual", "memo", "notice", "order", "permit", "policy",
    "poster", "procedure", "protocol", "receipt", "record", "report",
    "schedule", "specification", "statement", "summary", "survey", "table",
    "ticket", "timeline", "voucher", "warning", "worksheet", "blueprint",
    "contract", "agreement", "proposal", "presentation", "analysis",
    "assessment", "evaluation", "review", "audit", "inspection", "certification",
    "registration", "application", "submission", "documentation", "portfolio",
    "profile", "database", "inventory", "catalog", "index", "reference"
]

# Locations
locations = [
    "workshop wall", "office door", "lab bench", "warehouse gate", "storefront window",
    "classroom wall", "cafeteria menu board", "cashier counter", "library entrance",
    "noticeboard", "lobby directory", "bus stop shelter", "pharmacy counter",
    "hospital corridor", "conference room", "train platform", "reception desk",
    "bulletin board", "factory floor", "loading dock", "storage room",
    "maintenance area", "service counter", "repair shop", "utility room",
    "equipment shed", "parts depot", "supply closet", "tool crib",
    "inventory room", "assembly line", "test chamber", "quality lab",
    "clean room", "inspection area", "calibration room", "greenhouse bench",
    "seedling tray", "irrigation panel", "fertilizer shed", "harvester cab",
    "storage silo", "drafting table", "model shop", "blueprint room",
    "materials library", "design studio", "presentation wall", "service bay",
    "parts counter", "diagnostic station", "tire rack", "tool cabinet",
    "wash bay", "teller window", "vault door", "safe deposit room",
    "loan office", "customer desk", "drive through", "research bench",
    "specimen cabinet", "microscope station", "culture room", "incubator area",
    "sample storage", "conference table", "meeting booth", "boardroom wall",
    "presentation screen", "executive desk", "reception lobby", "fume hood",
    "reagent shelf", "balance room", "distillation setup", "glassware cabinet",
    "waste storage", "courthouse steps", "city hall lobby", "polling booth",
    "voter registration", "community center", "public square", "weather station",
    "observation deck", "monitoring room", "data center", "research facility",
    "sensor array", "server room", "workstation cluster", "network cabinet",
    "coding lab", "development floor", "testing facility", "job trailer",
    "tool shed", "material yard", "equipment garage", "crane cab",
    "safety station", "prep kitchen", "pantry shelf", "spice rack",
    "recipe stand", "cutting station", "storage cooler", "gallery wall",
    "exhibit hall", "performance stage", "artist studio", "cultural center",
    "heritage site", "creative workspace", "prototype lab", "modeling room",
    "rendering station", "innovation hub", "design center", "trading floor",
    "market desk", "analysis room", "research center", "data visualization",
    "economic institute", "lecture theater", "study hall", "seminar room",
    "teaching lab", "learning center", "academic building"
]

# Text styles
text_styles = [
    "printed english text", "handwritten english text", "typewritten english text",
    "chalkboard english text", "marker pen english text", "laminated sign english text",
    "typed english text", "calligraphy english text", "embossed english text",
    "engraved english text", "digital display text", "LED screen text",
    "vinyl lettering text", "stenciled text", "painted text", "etched text",
    "carved text", "pressed text", "stamped text", "laser printed text",
    "dot matrix text", "thermal printed text", "inkjet printed text",
    "screen printed text", "embroidered text", "wooden sign text",
    "metal plate text", "plastic label text", "paper form text",
    "cardboard sign text", "glass window text", "ceramic tile text",
    "fabric banner text", "rubber stamp text", "wax crayon text",
    "pencil written text", "pen written text", "marker written text",
    "chalk written text", "paint marker text", "permanent marker text"
]

# Quality descriptors
quality_descriptors = [
    "sharp focus", "legible", "clear", "readable", "visible detailed view",
    "high resolution", "macro photography", "closeup photography", 
    "detailed photography", "flat lay photography", "visible text closeup",
    "readable text macro", "detailed scan", "high resolution scan",
    "macro scan", "closeup scan", "detailed view", "visible text",
    "readable text", "clear text closeup", "bold lettering",
    "fine print visible", "large text readable", "small text legible",
    "faded text visible", "worn text readable", "fresh text clear",
    "crisp text sharp", "blurred text readable", "highlighted text visible",
    "underlined text clear", "italicized text readable", "bold text visible",
    "uppercase text clear", "lowercase text readable", "mixed case visible"
]

def generate_pattern1_keywords(count):
    """Generate keywords following Pattern 1: location/context + text type + descriptions + visibility"""
    import random
    
    contexts = [
        "vintage", "historic", "modern", "contemporary", "antique", "classic",
        "industrial", "commercial", "residential", "municipal", "federal",
        "private", "public", "corporate", "academic", "medical", "legal",
        "financial", "retail", "hospitality", "manufacturing", "agricultural",
        "technological", "scientific", "educational", "cultural", "recreational"
    ]
    
    text_types = [
        "blueprint", "poster", "menu", "whiteboard", "sign", "label",
        "card", "form", "receipt", "invoice", "ticket", "pass",
        "certificate", "license", "permit", "notice", "warning",
        "instruction", "manual", "guide", "handbook", "directory",
        "schedule", "timetable", "calendar", "agenda", "checklist",
        "log", "record", "report", "document", "file", "folder"
    ]
    
    descriptions = [
        "scan with visible", "photo with readable", "closeup showing",
        "detailed view of", "macro shot of", "flat lay with",
        "high resolution", "detailed photography", "closeup photography",
        "scan showing", "image with", "photo showing", "view of"
    ]
    
    text_qualities = [
        "handwritten text", "printed text", "typed text", "digital text",
        "calligraphy text", "block letters", "cursive writing", "technical text",
        "numerical data", "alphabetical text", "mixed text", "formatted text"
    ]
    
    keywords = []
    for _ in range(count):
        context = random.choice(contexts)
        text_type = random.choice(text_types)
        desc = random.choice(descriptions)
        quality = random.choice(text_qualities)
        
        keyword = f"{context} {text_type} {desc} {quality}"
        keywords.append(keyword)
    
    return keywords

def generate_pattern2_keywords(count):
    """Generate keywords following Pattern 2: domain + document type + location + text style + quality"""
    import random
    
    keywords = []
    for _ in range(count):
        domain = random.choice(domains)
        doc_type = random.choice(doc_types)
        location = random.choice(locations)
        style = random.choice(text_styles)
        quality = random.choice(quality_descriptors)
        
        keyword = f"{domain} {doc_type} {location} {style} {quality}"
        keywords.append(keyword)
    
    return keywords

def main():
    # Generate approximately 3,500 of each pattern to reach ~7,000 total
    pattern1_keywords = generate_pattern1_keywords(3500)
    pattern2_keywords = generate_pattern2_keywords(3500)
    
    # Combine and write to file
    all_keywords = pattern1_keywords + pattern2_keywords
    
    with open('/Users/ahtisham/vqa_dataset_project/additional_keywords_remaining.txt', 'w') as f:
        for keyword in all_keywords:
            f.write(keyword + '\n')
    
    print(f"Generated {len(all_keywords)} additional keywords")
    print(f"Pattern 1: {len(pattern1_keywords)} keywords")
    print(f"Pattern 2: {len(pattern2_keywords)} keywords")

if __name__ == "__main__":
    main()