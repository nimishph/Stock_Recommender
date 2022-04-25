from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


def getDifferentialPE(sectorPE: float, companyPE: float) -> float:
    differentialPE = (sectorPE-companyPE)/(sectorPE)
    differentialPE = differentialPE*100
    return differentialPE


def calculateAvg(dict_: dict[str, list], label: str, index: int) -> list[float]:
    prev_values = dict_[label][0:index]
    values = dict_[label][index]
    avg = sum(values)/len(values)
    newValues = prev_values + [avg]
    return newValues


def toFloat(value: str, delimiter) -> float:
    float_value = 0
    try:
        float_value = float(value.replace(delimiter, ''))
    except ValueError:
        pass
    return float_value


def generateFundamentalCSV() -> pd.DataFrame:
    LABELS_1 = ["TICKER", "COMPANY_NAME", "SECTOR",
                "CAP_SIZE", "BETA", "DIVIDEND_YIELD", "SECTOR_PE"]
    LABELS_2 = ["EPS", "PRICE TO EARNING", "DIFFERENTIAL_PE",
                "INV_BETA", "SALES", "NET PROFIT", "EBITDA", "EBITDA_MARGIN"]

    dict_ = {label: [] for label in LABELS_1+LABELS_2}

    company_details = pd.read_csv("./Data/Company_Details.csv")

    for label in LABELS_1:
        dict_[label] = list(company_details[label])

    print("Generating fundamental csv with raw values...")
    for index in tqdm(range(len(dict_["TICKER"]))):
        # print(f"For ticker: {ticker}")
        ticker = dict_["TICKER"][index]
        df = pd.read_csv(f"./Data/Company_reports/{ticker}.csv")
        try:
            df = df.drop([12, 13, 14, 15, 16, 17, 18, 19, 20, 21], axis=0)
        except KeyError:
            pass
        try:
            df = df.drop(["Trailing", "Best Case", "Worst Case"], axis=1)
        except KeyError:
            pass
        column_labels = [str(x) for x in df]
        find_value = "17"
        for i, label in enumerate(column_labels):
            if find_value in label:
                start_index = i
                break

        rows, cols = df.shape
        for r in range(rows):
            values = list(df.iloc[r])
            key = values[0].upper()
            values = values[start_index:]
            values = [toFloat(x, ",") for x in values]
            if key not in dict_:
                dict_[key] = []
            dict_[key].append(values)

        ebitdas = []
        ebitda_margins = []

        for c in range(len(column_labels)-start_index):
            ebitda = dict_["NET PROFIT"][index][c] + dict_["TAX"][index][c] + \
                dict_["DEPRECIATION"][index][c] + dict_["INTEREST"][index][c]
            ebitda_margin = (ebitda*100)/dict_["SALES"][index][c]
            ebitdas.append(ebitda)
            ebitda_margins.append(ebitda_margin)

        dict_["EBITDA"].append(ebitdas)
        dict_["EBITDA_MARGIN"].append(ebitda_margins)
        dict_["EPS"] = calculateAvg(dict_, "EPS", index)
        dict_["PRICE TO EARNING"] = calculateAvg(
            dict_, "PRICE TO EARNING", index)
        dict_["DIFFERENTIAL_PE"].append(getDifferentialPE(
            dict_["SECTOR_PE"][index], dict_["PRICE TO EARNING"][index]))
        dict_["INV_BETA"].append(1/dict_["BETA"][index])

    final_dict = {}
    for key in dict_:
        if key in LABELS_1 + LABELS_2:
            if type(dict_[key]) == list:
                final_dict[key] = dict_[key]
    return pd.DataFrame(final_dict)


def normalize(label: str, dataFrame: pd.DataFrame) -> dict[str, list]:
    labelVal = {'L': [], 'M': [], 'S': []}
    for values, cap in zip(dataFrame[label], dataFrame["CAP_SIZE"]):
        labelVal[cap].append(values)

    for cap in labelVal:
        scaler = MinMaxScaler(feature_range=(1, 10))
        if type(labelVal[cap][0]) == float:
            data = np.array(labelVal[cap])
            data = data.reshape(-1, 1)
            temp = scaler.fit_transform(data)

        else:
            data = np.array(labelVal[cap])
            data = data.reshape(-1, 1)
            temp = scaler.fit_transform(data)
            temp = temp.reshape(-1, 3)
        labelVal[cap] = temp
    return labelVal


def getAvg(values):
    l = []
    l.append((values[-1]+values[-2])/2)
    l.append((values[-1]+values[-2]+values[-3]+values[-4])/4)
    l.append(sum(values)/5)
    return(l)


def getGrowthAvg(values):
    l = []
    g1 = (values[-1]-values[-2])/values[-2]
    g2 = ((values[-2]-values[-3])/values[-3])
    g3 = (values[-3]-values[-4])/values[-4]
    g4 = (values[-4]-values[-5])/values[-5]
    l.append(g1)
    l.append((g1+g2+g3)/3)
    l.append((g1+g2+g3+g4)/4)
    return(l)


def deriveAndNormalize(dataFrame: pd.DataFrame) -> pd.DataFrame:
    column_labels = [x for x in dataFrame]
    sales_index = column_labels.index("SALES")
    beta_index = column_labels.index("BETA")

    print("Calculating derivations [2y, 4y, 5y]...")
    for i in tqdm(range(sales_index, len(column_labels))):
        label = column_labels[i]
        avgFunction = getGrowthAvg if label == "SALES" else getAvg
        for j, cell in enumerate(dataFrame[label]):
            # temp = [float(x) for x in cell.strip("][").split(", ")]
            dataFrame[label][j] = avgFunction(cell)

    print("Normalizing dataset...")
    for i in tqdm(range(beta_index, len(column_labels))):
        label = column_labels[i]
        normalizedVal = normalize(label, dataFrame)
        for j, cap in enumerate(dataFrame["CAP_SIZE"]):
            val = normalizedVal[cap][0]
            normalizedVal[cap] = normalizedVal[cap][1:]
            dataFrame[label][j] = val

    return dataFrame


def appendPrices(dataFrame: pd.DataFrame) -> pd.DataFrame:
    price_df = pd.read_csv("./Data/prices.csv")
    label = list(price_df)[0]
    dataFrame[label] = price_df[label]
    return dataFrame


def generateDataset():
    fundamentals_df = generateFundamentalCSV()
    pd.DataFrame.to_csv(fundamentals_df, "./fundamental_raw.csv", index=False)
    normalized_df = deriveAndNormalize(fundamentals_df)
    pd.DataFrame.to_csv(normalized_df, "./derived_normalized.csv", index=False)
    final_df = appendPrices(normalized_df)
    pd.DataFrame.to_csv(final_df, "./final_dataset.csv", index=False)


generateDataset()
