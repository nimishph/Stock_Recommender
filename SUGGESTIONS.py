from __future__ import annotations
import pandas as pd
weights = {
    "L": {
        # inverse beta for low risk
        'INV_BETA': [0.155, 0.1536, 0.1515],  # inverse
        'NET PROFIT': [0.15, 0.1502, 0.1505],
        'EBITDA': [0.145, 0.1452, 0.1455],
        'DIFFERENTIAL_PE': [0.14, 0.1402, 0.1405],
        'DIVIDEND_YIELD': [0.135, 0.1352, 0.1355],
        'EBITDA_MARGIN': [0.13, 0.1302, 0.1305],
        'EPS': [0.0725, 0.0727, 0.073],
        'SALES': [0.0725, 0.0727, 0.073],
    },
    "M": {
        # use difference from mean beta
        'EBITDA': [0.155, 0.155, 0.155],
        'NET PROFIT': [0.15, 0.15, 0.15],
        'EBITDA_MARGIN': [0.145, 0.145, 0.145],
        'DIVIDEND_YIELD': [0.14, 0.14, 0.14],
        'DIFFERENTIAL_PE': [0.135, 0.135, 0.135],
        'EPS': [0.092, 0.0917, 0.0911],
        'BETA': [0.0915, 0.09165, 0.09195],
        'SALES': [0.0915, 0.09165, 0.09195],
    },
    "H": {
        'BETA': [0.155, 0.1536, 0.1515],
        'NET PROFIT': [0.15, 0.1502, 0.1505],
        'EBITDA': [0.145, 0.1452, 0.1455],
        'SALES': [0.14, 0.1402, 0.1405],
        'EPS': [0.135, 0.1352, 0.1355],
        'DIFFERENTIAL_PE': [0.092, 0.0922, 0.0925],
        'DIVIDEND_YIELD': [0.0915, 0.0917, 0.092],
        'EBITDA_MARGIN': [0.0915, 0.0917, 0.092],
    }
}
ratios = {  # Large, Mid, Small
    "L": [[8, 1, 1], [6, 2, 2], [5, 3, 2]],
    "M": [[7, 2, 1], [5, 3, 2], [3, 4, 3]],
    "H": [[5, 3, 2], [4, 3, 3], [2, 3, 5]]
}


def getSuggestions(risk: str, period: int,  pref_sectors=[], dividend=False) -> dict[str, list]:
    current_ratio = ratios[risk][period]
    current_ratio_dict = dict(zip(["L", "M", "S"], current_ratio))
    current_weights = {}
    for factor, values in weights[risk].items():
        current_weights[factor] = values[period]

    results = {"L": [], "M": [], "S": []}
    df = pd.read_csv('./final_dataset.csv')
    raw_df = pd.read_csv('./fundamental_raw.csv')

    for i, cap in enumerate(df["CAP_SIZE"]):
        score = 0
        if len(pref_sectors) == 0 or df["SECTOR"][i] in pref_sectors:
            if dividend == False or df['DIVIDEND_YIELD'][i] > 1.0:
                for factor in current_weights:
                    if type(df[factor][i]) != str:
                        score += df[factor][i]*current_weights[factor]
                    else:
                        temp = [float(x)
                                for x in df[factor][i].strip("][").split()]
                        score += temp[period]*current_weights[factor]

                results[cap].append({"Symbol": raw_df["TICKER"][i], "Company name":  raw_df["COMPANY_NAME"][i],  "Sector": raw_df["SECTOR"][i],
                                    "CMP": f'₹{df["CURRENT_PRICE"][i]}', "Dividend Yield": raw_df['DIVIDEND_YIELD'][i], "Fundamental score": score})

    for cap in results:
        results[cap].sort(key=lambda x: x["Fundamental score"], reverse=True)
        results[cap] = results[cap][:current_ratio_dict[cap]]

    # for cap in results:
    #     print(cap, ": ")
    #     for elem in results[cap]:
    #         print("\t", elem)
    return results


# getSuggestions("L", 0, ['FMCG', 'Mining', 'Reality', 'Metals', 'IT'])
