
# FLASK APP CHUNK
from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)
#app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route('/home')
def index():
    # Need to create plot here
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>3D house builder</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    </head>
    <body>
    <div class="container">
    #there should be a 3D plot here!
    #Need to convert the 3D plot image using base64 encoding. Then load into html here!
    fig.write_html(f"{address_str}.html")
    </div>
    </body>
    </html>'''


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        address = request.form.get('address')
        if address == '$RESET':
            reset_templates()
            return '''
            <h1>Emptied the templates folder</h1>
            '''
        else:
            output_html = main(str(address))
            return render_template(output_html)

    # Landing page with user address form
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>3D house builder</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    </head>
    <body>
    <div class="container">
    <img src="./house.svg" alt="house"> 
    </div>
    <div class="container-fluid">
    <div class="jumbotron">
    <h1>3D house builder</h1>
    </div>
    <div class="container-fluid">
    <h4>This little app can build a 3D representation of any address in Flanders</h4>
    <p>Enter address</p>
    <form method='POST'>
    #<label id="address">Enter an address (in Antwerp, or this won't work!)</label>
    #<input id='address', type='text' name='address'/>
    <input type='submit' value='Submit'/>
    </p>
    </form>

    </div>
    </body>
    </html>'''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)

# <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
# <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
# use for warnings <div class="alert alert-danger">
# <img src="{{ url_for('plot', height=height, width=width) }}" />


# In[ ]:




