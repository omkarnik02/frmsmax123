from app import app
import warnings
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    app.run(debug=True, host='172.25.57.117',port=5000)
