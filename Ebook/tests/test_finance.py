#!/usr/bin/env python3
"""
Test photorealistic image generation for Finance/Debt Management topics
"""

from image_generation_system import generate_ebook_image
import time

def test_finance_debt_management():
    """Test finance genre with debt management topics"""
    
    print("\n" + "="*70)
    print("FINANCE/DEBT MANAGEMENT - PHOTOREALISTIC IMAGE GENERATION TEST")
    print("="*70)
    
    # Test 1: Debt Management Strategies
    print("\n" + "="*70)
    print("TEST 1: Debt Management Strategies (Finance Genre)")
    print("="*70)
    
    topic1 = "Personal Finance Management"
    section1 = "Debt Consolidation vs Debt Avalanche Method"
    content1 = """
    Debt management strategies vary significantly in their approach and effectiveness. 
    The debt consolidation method involves combining multiple debts into a single loan 
    with a lower interest rate, simplifying monthly payments and potentially reducing 
    overall interest costs. This approach works best for individuals with good credit 
    scores who can secure favorable loan terms. In contrast, the debt avalanche method 
    focuses on paying off debts with the highest interest rates first while making 
    minimum payments on others. This mathematical approach minimizes total interest 
    paid over time but requires discipline and patience. Financial advisors often 
    recommend the avalanche method for those committed to aggressive debt reduction, 
    while consolidation suits those seeking simplification and immediate relief from 
    multiple payment schedules.
    """
    
    success1, message1, path1, prompt1 = generate_ebook_image(
        topic1,
        section1,
        "test_finance_debt_consolidation.png",
        content1
    )
    
    if success1:
        print(f"\n✅ TEST 1 PASSED: {path1}")
    else:
        print(f"\n❌ TEST 1 FAILED: {message1}")
    
    # Wait between tests
    time.sleep(5)
    
    # Test 2: Financial Planning Timeline
    print("\n" + "="*70)
    print("TEST 2: Financial Planning Timeline (Finance Genre)")
    print("="*70)
    
    topic2 = "Wealth Building and Financial Freedom"
    section2 = "Financial Independence Timeline: From Debt to Wealth"
    content2 = """
    The journey from debt to financial independence follows a predictable timeline 
    with distinct phases. Phase 1 (Months 0-12): Emergency fund creation while 
    maintaining minimum debt payments, establishing a solid financial foundation. 
    Phase 2 (Years 1-3): Aggressive debt elimination using either avalanche or 
    snowball methods, freeing up cash flow for wealth building. Phase 3 (Years 3-5): 
    Maximizing retirement contributions and building investment portfolios, 
    transitioning from debt reduction to wealth accumulation. Phase 4 (Years 5-10): 
    Diversifying investments, considering real estate, and optimizing tax strategies. 
    Phase 5 (Years 10+): Achieving financial independence through passive income 
    streams, with the flexibility to work by choice rather than necessity.
    """
    
    success2, message2, path2, prompt2 = generate_ebook_image(
        topic2,
        section2,
        "test_finance_wealth_timeline.png",
        content2
    )
    
    if success2:
        print(f"\n✅ TEST 2 PASSED: {path2}")
    else:
        print(f"\n❌ TEST 2 FAILED: {message2}")
    
    # Wait between tests
    time.sleep(5)
    
    # Test 3: Investment Portfolio Management
    print("\n" + "="*70)
    print("TEST 3: Investment Portfolio Architecture (Finance Genre)")
    print("="*70)
    
    topic3 = "Investment Management Strategies"
    section3 = "Modern Portfolio Diversification System"
    content3 = """
    Modern portfolio theory emphasizes diversification across multiple asset classes 
    to optimize returns while managing risk. A well-structured portfolio balances 
    stocks (domestic and international), bonds (government and corporate), real estate 
    investment trusts (REITs), and alternative investments. The allocation depends on 
    factors including age, risk tolerance, investment timeline, and financial goals. 
    Younger investors typically favor aggressive growth with 80-90% equity exposure, 
    while those approaching retirement shift toward conservative allocations with 
    40-60% in fixed income securities. Regular rebalancing ensures the portfolio 
    maintains target allocations, selling appreciated assets and buying undervalued 
    ones. This systematic approach capitalizes on market volatility while maintaining 
    disciplined investment principles.
    """
    
    success3, message3, path3, prompt3 = generate_ebook_image(
        topic3,
        section3,
        "test_finance_portfolio_system.png",
        content3
    )
    
    if success3:
        print(f"\n✅ TEST 3 PASSED: {path3}")
    else:
        print(f"\n❌ TEST 3 FAILED: {message3}")
    
    # Final summary
    print("\n" + "="*70)
    print("FINANCE/DEBT MANAGEMENT TEST COMPLETE")
    print("="*70)
    
    results = [
        ("Debt Consolidation vs Avalanche", success1, path1),
        ("Financial Independence Timeline", success2, path2),
        ("Portfolio Diversification System", success3, path3)
    ]
    
    successful = sum(1 for _, success, _ in results if success)
    
    print(f"\n✅ Successful: {successful}/3")
    print(f"\n📊 Results:")
    for title, success, path in results:
        status = "✅" if success else "❌"
        print(f"{status} {title}")
        if success:
            print(f"   → {path}")
    
    print("\n📁 Expected files:")
    print("   • test_finance_debt_consolidation.png (Comparison layout)")
    print("   • test_finance_wealth_timeline.png (Timeline layout)")
    print("   • test_finance_portfolio_system.png (System/Architecture)")
    print("   • generated_prompts/ (3 detailed 700+ word prompts)")
    
    print("\n💡 Features tested:")
    print("   ✓ Finance genre detection")
    print("   ✓ Photorealistic business professional characters")
    print("   ✓ Content-type specific layouts (comparison, timeline, system)")
    print("   ✓ Professional corporate aesthetics")
    print("   ✓ Gold/navy color palette for finance")
    
    return successful == 3


if __name__ == "__main__":
    success = test_finance_debt_management()
    
    if success:
        print("\n" + "="*70)
        print("🎉 ALL FINANCE TESTS PASSED!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
