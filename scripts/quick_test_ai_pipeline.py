# scripts/quick_test_ai_pipeline.py

from app.database.queries import get_all_products  # o la tua funzione equivalente
from app.flows.flow_ai_pricing.b_pricing_ai_pipeline import simulate_new_prices_with_ai

def main():
    products = get_all_products()
    if not products:
        print("Nessun prodotto nel DB.")
        return

    # prendi pochi prodotti per test veloce
    sample = products[:3]

    result = simulate_new_prices_with_ai(sample)

    print("\n=== QUICK AI PIPELINE TEST ===")
    for r in result:
        print(
            f"- id={r['id']} sku={r['sku']} name={r['name']} "
            f"base={r['base_price']} engined={r['engined_price']} "
            f"coeff={r['ai_coefficient']} final={r['final_price']}"
        )

if __name__ == "__main__":
    main()
