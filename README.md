# Download UPI Equity End of Date T+1

## 0. Check out the code

```powershell
git checkout https://github.com/y5mei/DSB_records.git
cd .\DSB_records\ 
```

## 1. Create a virtual env and install dependency


```powershell
python -m venv .venvdsb
.\.venvdsb\Scripts\Activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. If you don't have chrome driver yet, install it from [here](https://googlechromelabs.github.io/chrome-for-testing/#stable)

After installation, You want to make sure chromedriver is indeed in your OS's path: i.e.:

When you run which, you should see this kind of printout in your terminal:

```powershell
(.venvdsb) PS C:\Users\Zhuzhu\PyCharmMiscProject> which chromedriver
C:\EnvironmentVariables\ChromeDriver\chromedriver.exe
```

## 3. Run the crawler script 

```powershell
python .\script.py --date=20250101 --email=<your_email> --password=<your_password>
```

The downloaded file should be in your browser's default downloaded dir.