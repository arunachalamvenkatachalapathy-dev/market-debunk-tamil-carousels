import os
import sys
from pathlib import Path
from PIL import Image

# Add project root to path
repo_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_path))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.validator import CarouselValidator
from src.image_director import ImageDirector

def test_offline_render():
    deck = {
        "caption": "Test Tanglish caption with save and share cta",
        "slides": [
            {
                "role": "hook",
                "slide_index": 1,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["Mutual Fund-ல்", "<span class='highlight-box'>₹34 Lakhs Loss-ஆ?!</span>", "உண்மை என்ன?"]
            },
            {
                "role": "value_1",
                "slide_index": 2,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["Retail முதலீட்டாளர்களின்", "<span class='highlight-box'>மாயை & உண்மை</span>"],
                "comparison_data": {
                    "myth": "Regular mutual fund-ல் distributor நமக்கு நல்ல guidance தருவார், அதனால கூடுதல் லாபம் கிடைக்கும்.",
                    "reality": "Regular plan-ல் ஆண்டுதோறும் <strong>1.0% to 1.5% commission</strong> கழிக்கப்படுவதால், Direct plan-ஐ விட பெரிய இழப்பு ஏற்படும்."
                }
            },
            {
                "role": "value_2",
                "slide_index": 3,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["மறைக்கப்பட்ட 1% கட்டணத்தின்", "<span class='highlight-box'>அதிர்ச்சி உண்மை</span>"],
                "stat_data": {
                    "badge": "VERIFIED MARKET IMPACT",
                    "metric": "₹34 Lakhs",
                    "label": "20 ஆண்டுகளில் ஏற்படும் இழப்பு",
                    "context": "மாதம் ₹25,000 SIP-ல் 12% கூட்டு வட்டியில் 20 வருடங்கள் முதலீடு செய்யும் போது, 1% commission-ஆல் <strong>₹34.8 Lakhs</strong> இழப்பு ஏற்படுகிறது."
                }
            },
            {
                "role": "value_3",
                "slide_index": 4,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["Smart Money", "<span class='highlight-box'>Liquidity-ஐ எப்படி</span>", "பயன்படுத்துகிறது?"],
                "flowchart_data": [
                    {"step": 1, "title": "செய்தி வெளியீடு", "text": "Hype செய்திகள் வந்தவுடன் retail buyers சந்தையில் நுழைகிறார்கள்."},
                    {"step": 2, "title": "Liquidity Dump", "text": "Smart Money தங்கள் பங்குகளை அதிக விலையில் விற்கிறது."},
                    {"step": 3, "title": "விலை சரிவு", "text": "சந்தை உடனே சரிந்து retail traders மாட்டிக் கொள்கிறார்கள்."}
                ]
            },
            {
                "role": "value_4",
                "slide_index": 5,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["Compounding இழப்பின்", "<span class='highlight-box'>உண்மை தாக்கம்</span>"],
                "card_text": "சந்தையில் 50% நஷ்டம் ஏற்பட்டால், மீண்டும் சமநிலைக்கு வர <strong>100% லாபம்</strong> தேவை. முதலீட்டை காப்பதே முதல் விதி."
            },
            {
                "role": "value_5",
                "slide_index": 6,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["முதலீட்டை காக்கும்", "<span class='highlight-box'>முக்கிய விதி</span>"],
                "card_text": "செய்திகளை பார்த்து trade செய்யாதீர்கள். ஒரே வர்த்தகத்தில் <strong>2%-க்கு மேல்</strong> capital risk செய்யாதீர்கள்."
            },
            {
                "role": "value_6",
                "slide_index": 7,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["Pre-Trade", "<span class='highlight-box'>Capital தணிக்கை</span>"],
                "checklist_data": [
                    {"status": "fail", "text": "Hype-ஐ பார்த்து blind-ஆ market order போடுவது."},
                    {"status": "pass", "text": "Delivery volume மற்றும் institutional flow-ஐ சரிபார்ப்பது."},
                    {"status": "pass", "text": "Trade-க்கு முன்பே strict stop-loss முடிவு செய்வது."}
                ]
            },
            {
                "role": "bookmark_save",
                "slide_index": 8,
                "tag": "#MARKETDEBUNK",
                "title_lines": ["பிற்காலத்திற்கு", "இந்த பதிவை", "<span class='highlight-box'>Save & Share</span>", "செய்யுங்கள்"],
                "cta_detail": "இந்த institutional risk checkpoints-ஐ உங்கள் அடுத்த trade-க்கு முன் review செய்ய Save செய்யுங்கள். உங்கள் நண்பர்களுக்கும் Share செய்து உதவுங்கள்."
            }
        ]
    }

    # 1. Validation test
    print("[TEST 1] Validating polymorphic deck in Tamil repo with CarouselValidator...")
    validator = CarouselValidator()
    is_valid, report = validator.validate_content(deck)
    print(f"Validation result: valid={is_valid}, report={report}")
    assert is_valid, f"Validation failed with report: {report}"
    print("✓ CarouselValidator PASSED in Tamil repo!")

    # 2. Offline Render test
    print("\n[TEST 2] Rendering polymorphic deck in Tamil repo via ImageDirector (Playwright)...")
    director = ImageDirector()
    result = director.render_carousel(deck, run_id="tamil_test_archetypes")

    png_paths = result.get("slide_png_paths", [])
    pdf_path = result.get("pdf_path")

    print(f"Rendered {len(png_paths)} slides. PDF path: {pdf_path}")
    assert len(png_paths) == 8, f"Expected 8 slide PNGs, got {len(png_paths)}"

    for idx, p in enumerate(png_paths):
        assert os.path.exists(p), f"Slide {idx+1} PNG does not exist at {p}"
        with Image.open(p) as img:
            assert img.size == (1080, 1350), f"Slide {idx+1} dimensions {img.size} != (1080, 1350)"
        print(f"  ✓ Slide {idx+1} confirmed: 1080x1350 px ({os.path.basename(p)})")

    assert pdf_path and os.path.exists(pdf_path), f"PDF does not exist at {pdf_path}"
    pdf_size = os.path.getsize(pdf_path)
    assert pdf_size > 10000, f"PDF file size too small: {pdf_size} bytes"
    print(f"  ✓ Multi-page PDF confirmed: {pdf_size} bytes ({os.path.basename(pdf_path)})")

    print("\n✅ ALL OFFLINE RENDERING UNIT TESTS PASSED IN TAMIL REPO!")

if __name__ == "__main__":
    test_offline_render()
