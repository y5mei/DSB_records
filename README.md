# Download UPI Equity End of Date T+1

## 0. Check out the code

```powershell
git clone https://github.com/y5mei/DSB_records.git
cd .\DSB_records\ 
```

## 1. Create a virtual env and install dependency


```powershell

# Step-1 Create a virtual python environment, name the folder as .venvdsb
python -m venv .venvdsb
# If you get error for Python was not found, try run this command with your absolute python3 path:
# C:\foo\bar\python3.11.exe -m venv .venvdsb

# Step-2 Active the virtual python environment
# Note that you might need to use different command based on your python version
# See: https://docs.python.org/3.11/library/venv.html#how-venvs-work
# You can abort this virtual environment by type `deactivate` in your powershell terminal at any time.
.\.venvdsb\bin\Activate.ps1

# Step-3 Upgrade pip and install dependencies
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. [Optional] I think you don't need this step if Chrome browser on your windows machine is new enough.


### Try to directly run setp-3 first, if you get any error about chrome driver, then download it from [here](https://googlechromelabs.github.io/chrome-for-testing/#stable)

Once downloaded, you want to make sure chromedriver is indeed in your OS's path: i.e.:

When you run which, you should see this kind of printout in your terminal:

```powershell
(.venvdsb) PS C:\Users\Zhuzhu\PyCharmMiscProject> which chromedriver
C:\EnvironmentVariables\ChromeDriver\chromedriver.exe
```

Or print all the directories in your powershell's Path, and make sure chrome driver is in one of these directories.

```powershell
$env:Path -split ';'
```

## 3. Run the crawler script 

```powershell
python .\script.py --date=20250101 --email=<your_email> --password=<your_password>
```

The downloaded file should be in your browser's default downloaded dir.
