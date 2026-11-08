# japan-tic-intervention-split

This backs my post "TLT: Japan Sold $88 Billion To Defend The Yen, And The Long End Didn't Flinch" (November 2026), and the shorter X version.

Everyone ran the same line this year: Japan sold Treasuries to defend the yen. The US Treasury's own data splits Japan's holdings into bills, bonds, net sales and price changes, and when you run that split most of the drop is bills and price. This repo is the split, the match against Japan's Ministry of Finance intervention reports, the 2022 and 2024 precedents, and the August gap: about 50bn of what MOF sold that month that doesn't show up anywhere in US data.

## How to run it

You need Python 3. No packages beyond the standard library.

```
cd scripts
python3 japan_split.py
python3 intervention_match.py
python3 who_took_the_bills.py
python3 long_end_test.py
python3 refill_after.py
python3 precedent_2024.py
python3 private_overlay.py
python3 custody_check.py
python3 funding_check.py
python3 yen_gains.py
python3 august_gap.py
python3 fefsa_composition.py
python3 intervention_gaps.py
python3 custody_centres.py
python3 error_band.py
python3 headline_vs_actual.py
python3 treasury_share.py
python3 event_study.py
python3 yen_persistence.py
python3 count_thresholds.py
python3 capacity_countdown.py
python3 sept_securities.py
python3 reserve_template.py
python3 auction_runoff.py
python3 fed_lines.py
python3 yen_history.py
python3 tlt_convexity.py
python3 tlt_target.py
python3 cftc_positioning.py
python3 tlt_flows.py
python3 tlt_options.py
python3 term_premium.py
python3 auction_test.py
python3 auction_20y_check.py
python3 coupon_episode.py
python3 refill_2024_control.py
python3 tlt_band_history.py
python3 buybacks_tlt.py
python3 tlt_premium.py
python3 tlt_fails.py
python3 fed_soma_tlt.py
python3 mof_q3_check.py
python3 funding_waterfall.py
python3 official_flows.py
python3 coupon_supply.py
python3 intervention_history.py
python3 tieout.py
python3 crosscheck_sources.py
```

Every script reads from `data/` relative to its own folder, so you can run them from anywhere. Output CSVs land in `results/`.

## What each script gives you

- `japan_split.py` splits the fall in Japan's holdings, end-February to end-August 2026: bills down 120.4bn (sold or left to mature), price change on bonds minus 34.7bn, bonds and notes sold 12.8bn, other 3.1bn, total minus 171.0bn. Same split for China, all foreign official holders and all foreigners.
- `intervention_match.py` lines up the two MOF interventions with the month they settled in and compares MOF's reserve report, TIC for Japan and TIC for all foreign official holders. About 171.6bn of dollars sold, MOF foreign currency reserves down 170.2bn, Japan bills down 108.7bn, Japan bonds up 9.0bn, and the 63.7bn of MOF securities the Japan TIC row doesn't show.
- `who_took_the_bills.py` is bill supply against who bought: bills outstanding up 440.0bn, foreign official selling 141.1bn, Fed bills up 212.7bn (37%, 1.51 times official selling), 368.4bn left for private buyers.
- `long_end_test.py` is the 30-year yield across each intervention window (+1bp, -2bp) and across the window with no intervention (+49bp to 5.67%).
- `refill_after.py` is 2024 month by month. May 2024, the first intervention month: bills down 24.0bn, bonds up 0.2bn. July 2024 had a second intervention (11 and 12 July): bills down 3.0bn, bonds down 10.9bn. The three months with no intervention, June, August and September: bills up 43.4bn, bonds down 88.1bn. Also July 2026, between this year's two interventions.
- `precedent_2024.py` is the 2024 intervention month itself.
- `private_overlay.py` takes the private investors out of the Japan row using MOF's own monthly survey by investor type, for 2022, 2024 and 2026. August 2026: private Japanese flat on foreign bonds (minus $0.9bn), so the non-private bond flow is +11.9bn to +12.8bn. May 2026: private buying of $19.5bn leaves room for up to $22.4bn of hidden MOF bond sales. Sep-Oct 2022: the Japan row sold $67.5bn of bonds, private selling explains at most $37.1bn.
- `custody_check.py` is the New York Fed's weekly custody account for foreign official holders: down 55.4bn and 41.4bn in the two windows, and down 46.6bn more from 26 August to 28 October with no Japanese intervention.
- `yen_gains.py` is the yen side. MOF's foreign exchange fund had a Y50.25tn FX translation gain at 31 March 2025 (FEFSA financial statements). At JRI's estimated 115 break-even, selling at 156.7 and 159.2 this year books about Y7.4tn of gain (Y6.5tn at 120, Y8.3tn at 110).
- `crosscheck_sources.py` pulls the load-bearing numbers from a second publication and fails if they disagree: TIC table 3 against FRED, Fed bills and custody on FRED against the H.4.1 pages, the 30-year on FRED against Treasury's par curve, USD/JPY on FRED against the ECB's reference rates, SOFR on FRED against the New York Fed's own API, MOF's English reserve page against its Japanese one, the ECB's monthly API series against the 12-month totals in its own press release (EUR 659bn and EUR 412bn), and Japan's BoP reserve outflow against MOF's intervention reports for the same month. It also prints the FIMA line: on the H.4.1 week averages between 30 April and 29 October it never tops $1 million, and on FRED's Wednesday levels (H41RESPPALGTRFNWW) it never tops $2 million from 1 April to 4 November. Careful with FRED's WORAL: that's all repo, including the standing repo facility, so it jumps at quarter-end and isn't FIMA.
- `funding_check.py` is SOFR minus IORB by month in 2026 (minus 6.4bp in May, minus 0.8bp in August) next to the Treasury's cash account and bank reserves across each window. In the May window the TGA fell 152bn and reserves rose 148bn, so May's calm proves very little. In August the TGA rose 40bn and reserves fell 60bn.
- `august_gap.py` is the August gap. MOF securities down 87.8bn, Japan's Treasury row minus 37.0bn, agencies minus 2.1bn and corporates plus 1.1bn from TIC table 1, so 49.7bn matches nothing in US debt (50.8bn against Treasuries alone). Japan's preliminary balance of payments books minus Y15.09tn of reserve-asset transactions, 95.0bn at August's average rate, against a 94.6bn fall in the stock, so price is about 0.4bn. Private Japanese sold 0.9bn of long-term and 6.4bn of short-term foreign debt. Then the ECB's monthly balance of payments: non-residents bought a net EUR 2.2bn of euro-area debt in August 2026, against an August average of minus EUR 6.2bn (standard deviation 23.5bn) from 2014 to 2025. May 2026 had a smaller gap, 12.9bn. That's the gap on the change in holdings. The post uses the transactions basis from `intervention_gaps.py`: the BoP outflow less the 6.9bn deposit drop is 88.1bn sold, less 37.0bn of Treasuries and 1.1bn of agencies and corporates, leaves 50.0bn.
- `error_band.py` takes each way the August gap could be a measurement error and works out how big it would have to be to close the whole 49.7bn: price (BoP says +0.4bn, ruled out), TIC long-term figures (4.9% of Japan's holdings in one month, and they've been reported trades since February 2023), bill figures (62% of Japan's end-July bills), custody elsewhere (see `custody_centres.py`), timing (ruled out), interest income (wrong sign) and private Japanese swapping non-US bonds into Treasuries (can't rule out). `august_gap.py` also adds up every Japanese resident: 95.1bn of foreign debt sold in August, 38.0bn of it US, so 57.1bn of non-US debt left Japanese hands whoever sold it.
- `intervention_gaps.py` runs the August check for every intervention month since 2022 (September and October 2022, May and July 2024, May and August 2026), on transactions so price moves stay out: MOF's securities sold is Japan's BoP reserve-asset outflow less the change in deposits. In five of the six months MOF sold more than the Japan row's US debt flows can account for: 15.5bn in October 2022, 32.0bn in May 2024, 17.2bn in July 2024, 17.4bn in May 2026 and 50.0bn in August 2026, between 24% and 57% of what MOF sold. September 2022 goes the other way, because private Japanese were selling Treasuries hard. On the strict count that adds the private survey, all Japanese residents sold more than 5bn of non-US debt in four of the six. It also bounds the private swap with gross flows: in August 2026 hiding the gap would take Y8.0tn of switching, 74% of everything real-money investors (securities firms left out) bought in foreign bonds that month.
- `headline_vs_actual.py` tests the reading everyone uses: MOF's securities fell by X, so Japan sold X of Treasuries. Since 2024 that reading overstated the Treasuries TIC's Japan row actually sold in all four intervention months: between 17 and 58 points of the drop weren't Treasuries (Treasuries were 42% to 83% of it). This one is on the stock fall in the reserves report, because that's the number people read. The Treasury share below takes price out. In 2022 it was close, 6% and 8%, but partly by accident: falling bond prices inflated the drop in September 2022 while private Japanese selling inflated the Treasury row. The counts in `intervention_gaps.py` without 2022: four of four months on MOF alone, three of four on the strict count.
- `treasury_share.py` is the Treasury share: Treasuries sold by TIC's Japan row as a share of what MOF actually sold in each intervention's settlement month. "Actually sold" is the BoP reserve-asset outflow less the change in deposits, so it's a transaction and price doesn't get in. The usual reading assumes 100%. It was 262% in September 2022 (private Japanese were dumping Treasuries themselves), 96% in October 2022, and 41%, 43%, 87% and 42% since 2024, so 13 to 59 points short of 100. It also prints the version on the reserves report's stock fall (47%, 81%, 83% and 42% since 2024). The two differ by price, most in July 2024, when bond prices rose and the stock fell much less than MOF sold.
- `treasury_share.py` also bounds the share for MOF alone. The Japan row mixes MOF with private Japanese investors, and MOF's survey doesn't say how much of their foreign debt flow was Treasuries, so I assume anywhere from none to all of it. The bounds: September 2022 162% to 262%, October 2022 54% to 96%, May 2024 41% to 64%, July 2024 14% to 43%, May 2026 87% to 112%, August 2026 34% to 42%. Under 100% even at the high bound in four of six months. May 2026 can't be told apart from the usual reading. It moves too much from month to month to use as a multiplier. It's a check after the fact.
- `count_thresholds.py` reruns the two counts at every threshold from 0 to 60bn. Five of six on MOF alone and four of six strict hold for any threshold up to 15bn, and break at 20bn.
- `yen_persistence.py` carries the event study to 20 and 60 business days after MOF's last trade, and splits solo from joint. The two solo defenses I can read cleanly faded: April-May 2024 and April-May 2026 kept 45% and 11% of the settlement-week USD/JPY move after 20 business days (29th and 34th percentile). The joint July 2026 defense, with the US Treasury alongside, kept 62% after 20 (16th percentile) and 95% after 60 (USD/JPY down 3.66%). It was also the biggest, at Y15.40tn, so one case can't separate the US joining from size. The others run into the next intervention or the August 2024 carry unwind, and the script flags them. If MOF traded later in August 2026 than 31 July, that episode's numbers include it.
- `sept_securities.py` asks whether MOF's $17.9bn securities fall in September 2026, with MOF out of the market, was price. With MOF's maturity mix, a range of durations, September's Treasury yield changes (2-year and 10-year both up 54bp) and 0% to 20% of the book in euros, price and currency come to a loss of 12.2bn to 24.6bn, which brackets the fall. The durations and the 20% are my choices. Japan's September BoP will settle it.
- `reserve_template.py` reads the parts of MOF's monthly reserves file nobody reads: it's the IMF's full template. MOF's long forward position in foreign currency against the yen was $20bn in every month since January 2024, August included, with no short position above $1 million. Securities lent or on repo ran $187bn to $189bn in July and August, with slightly more taken in as collateral, and rose only $2.2bn in August. Derivatives, marked to market, moved $0.18bn in August (between -$0.8bn and +$1.5bn since 2024). So no forward dollar sales and no hidden repo. Gold fell from $124.1bn to $113.6bn in September, which with the securities fall covers most of that month's $29.1bn drop in reserves.
- `auction_runoff.py` tests sold against left to mature, using Treasury's bill auction allotments by investor class since October 2009. Foreign and international buyers let $73.9bn more bills mature than they bought in May 2026, the biggest run-off in 201 months since January 2010, and more than the $61.0bn fall in foreign official bills in TIC. August was $25.2bn, the ninth biggest, about 60% of TIC's $42.2bn. June 2026, with no intervention, was third ($36.7bn), and Japan's bills fell $23.1bn that month in TIC, so not all of it is defense. The category includes foreign private buyers and only sees auctions.
- `fed_lines.py` checks the Fed's foreign repo pool, agency and MBS custody and foreign official deposits at the Fed across the two windows. All inside their normal four-week ranges since 2023: the repo pool moved -$17.8bn and +$19.1bn, agency custody -$6.4bn and -$2.9bn, deposits flat.
- `yen_history.py` widens the yen test to every yen-buying episode in MOF's file since 1997 plus July 2026, and compares each with windows that follow a USD/JPY rise at least as big as the one going in. Both joint defenses held a month on: June 1998 (14th percentile) and July 2026 (19th), and June 1998 was only Y0.23tn. Clean solo cases sat at the 17th, 51st, 37th and 48th (Dec 1997, Apr 1998, Apr-May 2024, Apr-May 2026). October 2022 and July 2024 look strong but run into the 10 November 2022 US CPI report and the August 2024 carry unwind. 1991-92 is left out: about two dozen small operations that run into each other. Uses `data/fred_DEXJPUS_1971.csv`.
- `tlt_target.py` is the TLT rating. I don't forecast long yields, so the target sits on the forward curve: on it every Treasury earns about the 1-year rate (4.39% on 4 November), less TLT's 0.15% fee, and the price falls by the income paid out (5.28% SEC yield), which gives $80.91, so $81. An unchanged curve gives $81.68. A target within 15% of the price is a Hold, so Hold while TLT is between $70.43 and $95.29, about 105bp higher or 100bp lower on long yields at TLT's 14.90-year duration and 321 convexity. There are no scenario weights. `tlt_band_history.py` asks history how often the band breaks instead. Inputs in `data/tlt_2026-11-04.csv` (iShares, with the close checked on Seeking Alpha and Nasdaq) and `data/treasury_par_curve_2026-11.csv`.
- `tlt_convexity.py` rebuilds TLT's convexity from its 47 bonds on 4 November (`data/tlt_holdings_2026-11-04.csv`, from the iShares holdings file): each bond repriced from its own yield for a parallel move. It gives 321 (years squared) and a duration of 15.10. iShares' own holdings file carries two measures per bond, and weighted by market value they give 15.10 (modified duration) and 14.90 (the effective duration it quotes), so the gap is between those two measures, not a data error.
- `tlt_flows.py` is TLT's own positioning. Shares outstanding times NAV from iShares' daily history (`data/ishares_tlt_history_2026-11-05.csv`): about $5.4bn of net creations from 29 July to end-August, shares 504.6m to 570.4m, then 599.3m on 5 November. Short interest 111.6m shares on 15 October, 18.6% of shares outstanding (26.3% at end-2025), from FINRA with Nasdaq matching. The November payout annualizes to 5.04%.
- `tlt_options.py` reads Cboe's delayed TLT chain at the 5 November close: put/call open interest 0.51, one-month 25-delta skew -0.9 vol points (puts cheaper than calls).
- `auction_test.py` asks whether central banks stepped back at long-bond auctions. Every 20- and 30-year nominal auction since 2022 (116), from TreasuryDirect with FiscalData matching on indirect awards. The 35 auctions during a defense or in the four months after are set against the rest of the same tenor. During: median indirect-share percentile 52 over 13 auctions, none in the bottom tenth. Refill months: median 80. The oddity: the September and October 2026 20-years had the lowest and third-lowest indirect shares of 58 since 2022 (52.5%, 58.2%; February 2026 was second) and the highest direct shares since 2022, while the 30-years were near the top. Both bonds together, September and October sit at the 82nd and 55th percentile of normal months.
- `auction_20y_check.py` tries the easy explanations for the 20-year gap. FIMA non-competitive awards were zero at every bond auction since 2021, and SOMA add-ons sit outside the competitive award. The 20-year yielded 4 to 5bp more than the 30-year on those days, against a median 8bp on 20-year auction days since 2022, and a smaller discount goes with fewer indirect bids (correlation -0.46 over 58 auctions). Allow for that and September and October are still in the bottom 5% of residuals. September ranks lowest and October third lowest of 58 20-year auctions since 2022. Two of the bottom three landing back to back happens about 10% of the time by chance. Unexplained so far.
- `coupon_episode.py` splits out July 2024, the one defense since 2024 paid mostly with notes and bonds (Japan row bills -$3.0bn, notes and bonds -$10.9bn in July, -$22.3bn more in August). Its 30-year auctions were the weakest in any defense window: indirect share at the 12th percentile on 11 July, dealers at the 98th on 8 August. The 20-year on 17 July was at the 98th for indirect, the 30-year yield fell 8bp over the intervention days, and TLT never traded more than 1.9bp below NAV. Confounds: June CPI on 11 July 2024, the carry unwind on 5 August 2024. With 13 auctions in the windows, the chance that at least one is this weak by luck is 81% (indirect) and 23% (dealers), so it's a preview, not evidence. And the Japan row isn't MOF: the bounds put MOF's own Treasury sales that July at $4.4bn to $13.9bn of the row's $13.9bn, against $32.1bn of securities MOF sold.
- `refill_2024_control.py` checks the 2024 refill against the front end. End-May to end-September 2024 the 2-year fell 123bp and the 30-year 51bp, with the Fed's 50bp cut on 18 September 2024 inside the window. On every four-month window since 1977 (FRED DGS2 and DGS30, full history) the fit says the 30-year should have fallen about 67bp, so it lagged by 16bp, the 68th percentile of residuals (19bp and 60th on easing windows only). The ACM term premium fell 12bp.
- `tlt_band_history.py` runs every 12-month change in the 30-year since February 1977 through TLT's numbers today. TLT ends in the Hold band 86.2% of the time since 2000 (Buy 5.3%, Sell 8.5%) and 73.3% since 1977 (11.7%, 15.0%). It lands in my ledger's tighter band 69.5% of the time since 2000.
- `buybacks_tlt.py` reads Treasury's buyback files. In the 20-to-30-year liquidity bucket holders offered $19.9bn to $30.5bn an operation from June to August, when Treasury took $2bn, and $10.5bn to $14.9bn in the three since 24 September, all below the median since June 2024, while Treasury took $4.1bn to $6.0bn. The offered-to-accepted ratio fell mostly because Treasury bought more, so I lead with offers. $57.3bn of the $65.1bn bought back since June 2024 was in bonds TLT holds now, which says little, since TLT holds nearly every bond in that bucket. The post doesn't use it.
- `tlt_premium.py`: TLT's close against its NAV on 45 intervention and settlement days since 2022, -3.4 to +28.7bp, against a normal 5th-95th range of -1.0 to +14.3bp. Bond-market holidays are dropped because the NAV goes stale.
- `tlt_fails.py`: SEC fails to deliver in TLT (2022 to mid-October 2026). Ten-day peaks after each intervention, against every ten-day window: 65, 79, 95, 21, 26 and 31st percentile. The 95 is one day in May 2024 (3.2m shares).
- `fed_soma_tlt.py`: the Fed holds $566.9bn of TLT's 47 bonds, 19.0% of what's outstanding and 8.6 times TLT's own par, up $36.3bn in a year, all of it the Fed's share of four bonds first sold during the year. Its holdings of the other 43 didn't change. Its 28 October implementation note rolls over all Treasury principal at auction, so nothing runs off.
- `mof_q3_check.py` is ready for MOF's July to September 2026 daily file. Save the new file over `data/mof_intervention_history.csv` and run it. It prints each day's currency pair and whether any day sold something other than dollars for yen.
- `term_premium.py`: 10-year term premium 0.68% on ACM (New York Fed, 3 November) and 0.91% on Kim-Wright (Fed Board via FRED, 30 October). They disagree on whether it rose in 2026, so I quote both.
- `cftc_positioning.py` reads the CFTC's Traders in Financial Futures report for 27 October 2026. Leveraged funds were net short 805,828 Ultra bond and 150,393 classic bond contracts, about $95.6bn of face value; asset managers net long 858,168 and 383,981. I read that as the basis trade. The CFTC doesn't label it, so that's an inference.
- `capacity_countdown.py` counts how many August-sized defenses (Y15.40tn, 97.3bn at 158.25) MOF could fund from bills, the FIMA cap and deposits before it has to sell notes and bonds. With 24% of each defense coming from paper outside the US: 0.4 from bills alone, 1.2 adding FIMA, 3.3 adding every dollar of deposits. Deposits stayed between about 155bn and 162bn from March 2024 to September 2026 through four interventions, so the top row flatters MOF. FIMA is a loan.
- `custody_centres.py` asks whether the August gap could be Treasuries MOF held with a custodian outside Japan, which TIC would put under that country. The usual custody centres (the UK, Belgium, Luxembourg, Switzerland, Ireland, Guernsey, Jersey, the Caribbean centres, Hong Kong and Singapore) were net buyers of 21.4bn in August. Every bill or bond line that fell among them adds to 22.8bn, and every other country that was a net seller, China included, adds 28.5bn. So hiding 50bn there needs nearly all of that to be MOF, with nobody else in those countries selling. The list of centres is my call and it's at the top of the script.
- `event_study.py` measures what moved across six interventions, on the intervention days and over the settlement week, against every other window of the same length from 2022 to October 2026. Since 2024 the yen strengthened every time (USD/JPY down 1.4% to 3.9% over the settlement week), the 30-year stayed inside its normal range every time (minus 14bp to plus 5bp), one-month bills cheapened 1bp to 6bp against SOFR, and euro-area government yields fell 2bp to 10bp. Against the US 10-year, euro yields moved minus 6bp to plus 9bp with no consistent sign, so nothing unusual, and this test can't tell euro selling the market absorbed from no euro selling at all. Small sample, and some days carried other news (1 May 2024 FOMC, 11 Jul 2024 CPI). The July 2026 episode is dated 30 and 31 July but sized at the full Y15.40tn window, so if some of that traded later in August its per-$10bn numbers are too small.
- `funding_waterfall.py` sizes the next defense at Y5tn, Y10tn and Y15tn at the ECB's 4 November rate (158.25), with bills capped at what Japan holds and the outside-US and deposit shares set by the 2024-26 range. At Y15tn, between 3.6bn and 40.7bn is left for coupons or the Fed's FIMA line; a July-2024-style mix would sell 32.6bn of coupons. The same model is in `Japan next-defense funding model.xlsx` alongside the post.
- `official_flows.py` is the general version of the check for any central bank, a TIC-only screen for Korea, Taiwan, Switzerland and India, and `data/country_data_map.csv`, which says what each one publishes and what still has to be confirmed.
- `fefsa_composition.py` reads MOF's annual breakdown of the FX fund's foreign assets. At 31 March 2025, 74% of its foreign securities were government bonds and 26% weren't, and 30.5% matured within a year (37.7% in one to five years, 31.8% after five). There's no currency split. Interest on securities and deposits comes to about 1.7bn dollars a month.
- `coupon_supply.py` sizes the 65.4bn bills can't cover against note and bond auctions in August and September 2026: 722bn of auctions, 361bn a month, 84bn of 20-year and longer. 65.4bn is 18% of one month.
- `intervention_history.py` reads MOF's own file of every intervention since April 1991. 2022: Y9.19tn (22 September, 21 and 24 October). 2024: Y15.32tn including Y5.53tn on 11 and 12 July. All 42 yen-buying days in the file sold dollars.
- `tieout.py` checks the pieces add back to the totals, that MOF's reserves fell by about what it spent, that the trades settled the month after, and that every number in the post comes out of the data. If it fails, the post is wrong somewhere.

## Data

- `data/slt_table3.txt`: US Treasury TIC, SLT table 3, "U.S. Treasury Securities Held by Foreign Residents", October 16 2026 release, data to August 2026. https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table3.txt
- `data/mof_interventions.csv`: MOF monthly intervention totals, each row with its page. https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/index.html
- `data/mof_intervention_days_2026q2.csv` and `data/mof_intervention_days_2024q2.csv`: MOF's quarterly daily breakdowns. https://www.mof.go.jp/english/policy/international_policy/reference/feio/quarter/2026_2Qe.html and https://www.mof.go.jp/english/policy/international_policy/reference/feio/quarter/2024_2Qe.html
- `data/mof_reserves.csv`: MOF "International Reserves/Foreign Currency Liquidity", month-end, each row with its page. Deposits are the "Deposits with" line.
- `data/fred_WSHOBL.csv`: Fed SOMA bill holdings, Wednesday levels. https://fred.stlouisfed.org/series/WSHOBL
- `data/fred_DGS30.csv`: 30-year Treasury yield. https://fred.stlouisfed.org/series/DGS30
- `data/fred_DEXJPUS.csv`: yen per dollar, New York noon rate. https://fred.stlouisfed.org/series/DEXJPUS
- `data/fred_WORAL.csv`: Fed repo with foreign official accounts. https://fred.stlouisfed.org/series/WORAL
- `data/mof_sector_longterm_raw.csv` and `data/mof_sector_shortterm_raw.csv`: MOF "Purchases and Sales of Foreign Securities by Residents by Types of Investors", long-term and short-term debt, as published (Shift-JIS). https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/index.htm
- `data/fred_WMTSECL1.csv`: Treasuries held in custody at the NY Fed for foreign official accounts, Wednesday levels. https://fred.stlouisfed.org/series/WMTSECL1
- `data/fred_SOFR.csv`, `data/fred_IORB.csv`: https://fred.stlouisfed.org/series/SOFR and https://fred.stlouisfed.org/series/IORB
- `data/fred_FORLTTREASNET42609.csv`, `data/fred_FORSTTREASNET42609.csv`, `data/fred_FORSTTREASPOS42609.csv`: the same TIC Japan series on FRED, used for 2022 because table 3 shows Japan's 2022 flows as n.a. https://fred.stlouisfed.org/series/FORLTTREASNET42609
- `data/esf_statement_2026-08.pdf`: Treasury Exchange Stabilization Fund statement for August 2026. Note 2 has the $500 million yen purchase. https://home.treasury.gov/system/files/206/ESF-August-2026-FS-Trunc-Notes.pdf
- `data/h41_transcribed.csv`: Fed bills, NY Fed custody and foreign official repo (FIMA) week averages, transcribed from each weekly H.4.1 release, each row with its page.
- `data/treasury_par_curve_2026.csv`, `data/treasury_par_curve_2001.csv`: Treasury daily par yield curve. https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve
- `data/ecb_reference_rates_usd_jpy.csv`: ECB reference rates, EUR/JPY and EUR/USD. https://data.ecb.europa.eu/
- `data/nyfed_sofr_2026-05.json`, `data/nyfed_sofr_2026-08.json`: SOFR from the New York Fed's API. https://markets.newyorkfed.org/
- `data/fefsa.csv` and `data/fefsa_financial_statements_fy2024.pdf`: FEFSA balance sheet lines at 31 March 2025, JRI's break-even estimate (https://www.jri.co.jp/MediaLibrary/file/report/researchfocus/pdf/16927.pdf) and the FIMA cap as reported by Reuters.
- `data/slt_table1.txt`: US Treasury TIC, SLT table 1, all long-term US securities by type and country. https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table1.txt
- `data/mof_reserves_historical.csv`: MOF's full monthly reserves history since 2013. https://www.mof.go.jp/policy/international_policy/reference/official_reserve_assets/historical.csv
- `data/mof_bop_monthly_summary.csv`: MOF's monthly BoP summary (reserve assets in column 18, 100m yen). https://www.mof.go.jp/policy/international_policy/reference/balance_of_payments/bp_trend/bpnet/sbp/s-1/6s-1-4.csv
- `data/mof_fefsa_assets_fy2024.xlsx`: MOF's breakdown of the FX fund's foreign assets, FY2024, published 10 November 2025. https://www.mof.go.jp/policy/international_policy/reference/gaitametokkai/index.html
- `data/fred_FORLTAGCYNET42609.csv`, `data/fred_FORLTCORPNET42609.csv`: Japan's net agency and corporate bond flows, the same TIC series on FRED, used because table 1 shows 2022 as n.a.
- `data/mof_bop_reserve_assets.csv`, `data/mof_bop_2026-05_preliminary.pdf`, `data/mof_bop_2026-08_preliminary.pdf`: MOF preliminary balance of payments, reserve assets line. https://www.mof.go.jp/policy/international_policy/reference/balance_of_payments/preliminary/bp202608.pdf
- `data/mof_intervention_history.csv`: MOF's full intervention record since April 1991, as published (Shift-JIS). https://www.mof.go.jp/english/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv
- `data/ecb_bps_nonresident_debt_purchases.csv`: ECB monthly balance of payments, euro area, non-residents' net purchases of euro-area debt securities, all sectors and general government, from 2014. Series keys like BPS.M.N.I10.W1.S1.S1.T.L.FA.P.F3.T.EUR._T.M.N.ALL. https://data.ecb.europa.eu/
- `data/ecb_bop_release_2026-08.pdf`: the ECB's press release for August 2026, for the 12-month totals. https://www.banque-france.fr/system/files/2026-10/ecb-press-release_20261020_Euro-area-monthly-balance-of-payments-August-2026.pdf
- `data/treasury_coupon_auctions_2026-08_10.json`: Treasury auction results for notes and bonds. https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/
- `data/fred_WTREGEN.csv`, `data/fred_WRESBAL.csv`: Treasury General Account and bank reserves, Wednesday levels. https://fred.stlouisfed.org/series/WTREGEN and https://fred.stlouisfed.org/series/WRESBAL
- `data/mspd_bills.json`: Treasury Monthly Statement of the Public Debt, bills outstanding. https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/

The Fed's purchase history (reserve management purchases at about $40bn a month from December 12 2025, $10bn a month after mid-April, zero from August 14, MBS paydowns rolled into bills) comes from the New York Fed's December 10 2025 operating statement and its later monthly schedules. It's context, no script uses it.

Japanese-language reading, for context (no script uses it): MOF's English statement of 3 August 2026 says Japan plans to use the Fed's FIMA repo facility in the future (https://www.mof.go.jp/english/public_relations/statement/others/20260803073000.html); the H.4.1 line never shows more than $2 million on any Wednesday from April to 4 November. The Japan Research Institute's 4 September 2026 report argues the yen effect of a FIMA-funded defense would be temporary (https://www.jri.co.jp/report/research/detail/16950/). Reuters on 7 September 2026, on the end-August reserves, wrote that the decline was led by foreign securities held mostly in Treasuries.

Sources for the thirteenth pass: Treasury investor class allotments, bills (https://home.treasury.gov/data/investor-class-auction-allotments, file October-7_2026-IC-Bills.xls, cleaned to `data/treasury_ic_bills_allotments.csv`); FRED WREPOFOR, WFASECL1, WDFOL, DEXJPUS from 1971; the June 1998 joint intervention in the New York Fed's report for April to June 1998 (https://www.newyorkfed.org/medialibrary/media/newsevents/news/markets/1998/fxq298.pdf).

Sources for the eighteenth pass: the FOMC statement of 18 September 2024 (https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm); FRED DGS2 and DGS30, full histories (`data/fred_DGS2_full.csv`, `data/fred_DGS30_full.csv`); FRED DGS20.

Sources for the sixteenth pass: TreasuryDirect auction results (https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type=Bond) and FiscalData's auctions query (https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/); FiscalData buyback operations and security details (https://fiscaldata.treasury.gov/datasets/treasury-securities-buybacks/); Nasdaq and Yahoo TLT closes; the New York Fed's SOMA holdings by CUSIP (https://markets.newyorkfed.org/api/soma/tsy/get/asof/2026-11-04.json and three earlier dates); the FOMC implementation note of 28 October 2026 (https://www.federalreserve.gov/monetarypolicy/files/monetary20261028a1.pdf); SEC fails-to-deliver files (https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data), TLT rows only, in `data/sec_ftd_tlt_2022_2026.csv`.

Sources for the fifteenth pass: iShares TLT holdings file and fund history (https://www.ishares.com/us/products/239454/ishares-20-year-treasury-bond-etf); FINRA consolidated short interest (https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest) and Nasdaq's copy (https://www.nasdaq.com/market-activity/etf/tlt/short-interest); Cboe delayed quotes (https://www.cboe.com/delayed_quotes/tlt/quote_table), one expiry checked against Nasdaq's option chain; the New York Fed's ACM term premium (https://www.newyorkfed.org/research/data_indicators/term-premia-tabs); FRED THREEFYTP10; Treasury's refunding statements of 4 November 2026 (https://home.treasury.gov/news/press-releases/sb0678/) and 5 August 2026 (https://home.treasury.gov/news/press-releases/sb0590), transcribed to `data/treasury_refunding_2026-11-04.csv`.

## Things to be careful with

How TIC builds its flows. Since February 2023 the long-term Treasury flows in table 3 come from purchases and sales reported on the SLT form. Form S was dropped after January 2023. The Fed staff note that explains the switch is https://www.federalreserve.gov/econres/notes/feds-notes/measuring-u-s-cross-border-securities-flows-out-with-the-old-in-with-the-new-20251015.html. Bill flows are different. Note 2 to table 3 says they're the month-over-month change in bill holdings, so bills that mature and aren't replaced count as sales. When I say Japan "ran down" its bills, that's why. The 2022 numbers come from before the switch.

TIC gets revised, and Treasury's annual survey of foreign holdings can move holdings between countries when it's folded in. The country numbers here are as published on 16 October 2026.

The Japan row in TIC is every Japanese resident, so MOF, life insurers, banks and pension funds are in one line. A private buyer can net out MOF selling in the same month.

TIC records securities by custody location. If MOF holds Treasuries with a custodian outside Japan, they show up under that country. I use the all-foreign-official total as the cross-check because it groups holders by type wherever they sit, and `custody_centres.py` adds up the custody rows themselves.

The Japan row bought 11.9bn of notes and bonds in August while private Japanese were net sellers of 0.9bn of long-term foreign bonds of every kind. Either MOF put about 12bn into coupons while it ran down bills, which TIC can't tell apart from private buying, or private investors bought Treasuries and sold other foreign bonds. The second is the swap, at about a quarter of the size it would need to close the gap. Public data can't separate them.

The July to August 2026 intervention has no daily breakdown yet, so I converted it at the July 30 and July 31 noon rates. The range is 96.6bn to 96.8bn and I use the middle.

The Fed bill number is the Wednesday nearest each date, not month-end.

The August gap is a finding by elimination. It isn't price (the BoP says so), it isn't other US securities (table 1), and the custody rows would need almost every falling line outside Japan to be MOF. That leaves securities issued outside the US. That doesn't have to mean outside the dollar: 26% of MOF's foreign securities aren't government bonds, and dollar bonds from supranationals or foreign agencies never show up in TIC. Euro bonds are the likeliest by size, but sterling, Aussie or Canadian paper would fit too. The euro-area numbers can't confirm it: a EUR 44bn seller fits inside a normal August. The ECB data have no country breakdown, so this is a test that could only have failed loudly, and it didn't. MOF's July to September daily breakdown will name the currency pair.

The private overlay assumes Japanese investors put between none and all of their foreign bond flows into Treasuries. If they sold Treasuries and bought euro bonds in the same month, MOF had more room to sell than the overlay shows. This matters most for 2024.

The 2022 and 2024 intervention amounts come from MOF's own historical file. An earlier version of my 2024 work called June to September 2024 a quiet refill. It wasn't, MOF intervened on 11 and 12 July 2024, and `refill_after.py` now splits July out.

The three calls in the post resolve on future TIC releases: Japan's bills up 10bn or more in the September TIC on November 18; September to December net bond sales above 40bn after taking out every yen of private Japanese foreign-bond flow as if it were Treasuries (`private_overlay.py`, with MOF's December survey); and the same measure above 20bn in the settlement month of any intervention of Y5tn or more before end-June 2027. The scripts here will rerun on the new file once you swap it into `data/`.

`yen_gains.py` is context the post no longer uses. The yen gain on dollars sold is the same whether MOF sells a bill or a bond, so it can't explain bills first. The 115 break-even is JRI's estimate from FEFSA's accounts, not an MOF figure, and the last audited balance sheet is 31 March 2025.

The funding test is weak. May's calm came with a 148bn reserve tailwind from the TGA drawdown after tax season.

The 30-year comparison uses Treasury's own par curve. Treasury didn't publish a 30-year rate from February 2002 to February 2006, so "highest since July 2001" is on Treasury's published curve. FRED's series fills the gap with an estimate and puts the last comparable close in July 2002.

TLT's convexity assumes every yield moves the same amount. The long end rarely does that exactly, and the fund turns over during the year. The scenario weights are mine. Short interest on TLT includes market makers' hedges and people shorting TLT against bonds they own, and options open interest doesn't say who's long, so neither is a clean bearish count.

The auction test reads indirect bidders as the place central banks show up, but the category also holds foreign private accounts and domestic funds bidding through dealers, and Treasury doesn't split it. Tails need the 1pm when-issued yield, which isn't free, so I don't measure them. Buyback offers are capped by how many offers each dealer may submit. Fails are listed only on days with a balance, so missing days count as zero.

The 4 November NAV is $81.738877 from iShares' fund history. It equals net assets over shares outstanding and matches iShares' published 0.03% premium.

## Corrections

None so far.
