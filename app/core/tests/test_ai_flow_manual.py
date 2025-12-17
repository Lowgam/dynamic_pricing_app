from app.database.queries import get_all_products
from app.core.services.pricing_engine import calculate_engined_price
from app.core.services.feature_builder import build_features  # o nome simile nel tuo file
from app.core.services.ai_engine import calculate_ai_coefficient  # adattalo al tuo nome reale
from app.core.services.pricing_engine import apply_engined_price

def manual_test_ai_flow():
    # 1) Take all products from DB and select one for testing
    products = get_all_products()
    if not products:
        print("No products found")
        return
    product = products[0]
    print("Test product:", product)

    # 2) Calculate engined price
    engined_price = calculate_engined_price(
        base_price=product["price"],
        cost_price=product["cost_price"],
        stock=product["stock"],
        sales_velocity= None,
        expiry_date_str=product["expiry_date"],
    )
    print("\nEngined_price:", engined_price)

    # 3) Building feature for AI
    features = build_features(product, engined_price)
    print("\nFeatures:", features)

    # 4) Calculate AI coeff (dict)
    ai_coefficient_and_reason = calculate_ai_coefficient(engined_price, features)
    print("\nAI coefficient and reason:", ai_coefficient_and_reason)
    coefficient = ai_coefficient_and_reason["coefficient"]
    print("\nCoefficient:", coefficient)

    # 5) Final price with coeff application
    final_price = apply_engined_price(engined_price, coefficient)
    print("\nFinal price:", final_price)


# 6) TESTING
if __name__ == "__main__":
    manual_test_ai_flow()