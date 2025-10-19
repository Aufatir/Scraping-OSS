Kalo ERORR fix sendiri gausa banyak tanya
hasilnya bakal ada di folder **data_nib**

Kalo proyeknya kosong isinya kaya gini :
{
        "nama_perusahaan": "XXXXXXXXXXX",
    "skala_badan_usaha": "Usaha Mikro",
    "projects_investment": {}
}

Kalo ada proyeknya :
{
    "nama_perusahaan": "XXXXXXXXXXXXXXXXX",
    "skala_badan_usaha": "Usaha Mikro",
    "projects_investment": {
        "R-XXXXXXXXXXXXX": 0,
        "R-XXXXXXXXXXXXXXX": 0,
        "R-XXXXXXXXXXXXXX1": 0,
        "R-XXXXXXXXXXXXXXXXXXXX": 5000000,
        "R-XXXXXXXXXXXXXXXXXXXX": 50000000,
        "R-XXXXXXXXXXXXXXXX": 50000000,
        "R-XXXXXXXXXXXXXXXXXXXX": 50000000,
        "R-XXXXXXXXXXXXXXXXXXXXX3": 5000000
    }
}

**Kadang BUG pas nyari perusahaan, itu tinggal jalanin ulang**

Install Kebutuhan :
pip install -r requirements.txt
playwright install
