x = {
  "id": "9a0ec0f9-3989-482b-9722-34d44912823e",
  "flights": [
    {
      "duration": 18000,
      "segments": [
        {
          "operating_airline": "ТЫ",
          "flight_number": "606",
          "equipment": "Boeing 767-200 Freighter",
          "cabin": "Economy",
          "dep": {
            "at": "2022-02-21T03:15:00+06:00",
            "airport": {
              "code": "ALA",
              "name": "Алматы"
            },
            "terminal": "1"
          },
          "arr": {
            "at": "2022-02-21T04:30:00+06:00",
            "airport": {
              "code": "USJ",
              "name": "Ушарал"
            },
            "terminal": "8"
          },
          "baggage": "20KG"
        },
        {
          "operating_airline": "ТЫ",
          "flight_number": "631",
          "equipment": "Boeing 757-300 with winglets",
          "cabin": "Economy",
          "dep": {
            "at": "2022-02-21T08:00:00+06:00",
            "airport": {
              "code": "USJ",
              "name": "Ушарал"
            },
            "terminal": "1"
          },
          "arr": {
            "at": "2022-02-21T11:45:00+06:00",
            "airport": {
              "code": "NQZ",
              "name": "Нур-Султан (Астана)"
            },
            "terminal": "4"
          },
          "baggage": "20KG"
        }
      ]
    },
    {
      "duration": 13500,
      "segments": [
        {
          "operating_airline": "ТЫ",
          "flight_number": "563",
          "equipment": "Airbus A340-600",
          "cabin": "Economy",
          "dep": {
            "at": "2022-02-22T03:25:00+06:00",
            "airport": {
              "code": "NQZ",
              "name": "Нур-Султан (Астана)"
            },
            "terminal": "2"
          },
          "arr": {
            "at": "2022-02-22T07:10:00+06:00",
            "airport": {
              "code": "ALA",
              "name": "Алматы"
            },
            "terminal": "8"
          },
          "baggage": "20KG"
        }
      ]
    }
  ],
  "price": {
    "amount": 120693,
    "currency": "KZT"
  },
  "refundable": True,
  "baggage": "20KG",
  "cabin": "Economy",
  "airline": {
    "code": "ТЫ",
    "name": "Tulpar Air",
    "logo": {
                "url": "https://avia-api.k8s-test.aviata.team/img/5805-57a5cfb89ab77b4a3c11ff3a5c7ff427.png",
                "width": 284,
                "height": 105
            }
  },
  "passengers": {
    "ADT": 1,
    "CHD": 0,
    "INF": 0
  },
  "type": "RT"
}
print(x["airline"]['logo']['url'])
