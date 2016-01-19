from flask import Flask, request, redirect, render_template, flash
from twilio.rest import TwilioRestClient
import twilio.twiml
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required, Length, ValidationError
import os
from twilio.util import TwilioCapability

app = Flask(__name__)




callers = {
	"+14085108793": "Jo",
	}

site_url = "http://e0c97f2d.ngrok.io/"
twilio_number = "+16509665991"
my_number = "+14085108793"

def fizzbuzz(value):
	output = ""
	for i in range(1,value+1):
		if i%3 == 0 and i%5 == 0:
			output += (' Fizz Buzz ')
		elif i%3 == 0:
			output += (' Fizz ')
		elif i%5 == 0:
			output += (' Buzz ')
		else:
			output += (' ' + str(i) + ' ')

	return output



def make_call(phoneNo):
	resp = twilio.twiml.Response()
	account_sid = 'ACe84df508961b0a4fc3e87dfe1de3077b'	
	auth_token =  'bc4ff778850349c5fb82b2dca3aa8409'
	client = TwilioRestClient(account_sid, auth_token)

	#make the call
	make_call = client.calls.create(to=phoneNo, from_=twilio_number, url=site_url)

	print make_call.account_sid
	return "Sucess"


def isValid(form, phoneNumber):
  rawTextField = str(phoneNumber)
  valueDesiredString = "value="
  valueIndex = rawTextField.index(valueDesiredString) +6
  numStr = rawTextField[valueIndex:len(rawTextField)-1]
  numStr = (numStr[1:13])
  print(numStr)
  print(len(numStr))
  if len(numStr)!= 12 or numStr[0] != "+" or not str.isdigit(numStr[1:13]):
      raise ValidationError("Your phone number isn't a valid US/Canada number")

class MySite(Form):
	failedCall = False
	phoneNumber = TextField('phoneNumber', validators=[Required(), Length(min=12, max=12), isValid])

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():

	
	from_number = request.values.get('From', None)
	

	if from_number in callers:
		caller = callers[from_number]
	else:
		caller = "there"

	resp = twilio.twiml.Response()

	resp.say("Hello " + caller, voice="alice", language="en-CA")


	with resp.gather(numDigits=2, action="/handle-key", method="POST") as g:
		g.say("Please enter a two digit number to play fizz buzz.", voice="alice", language="en-CA" )

	return str(resp)


@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
	"""Handle key press from a user. """

	#Get the digit pressed by the user
	digit_pressed = request.values.get('Digits', None)
	if digit_pressed.isdigit():
		user_input = int(digit_pressed)
		return_value = fizzbuzz(user_input)

		resp = twilio.twiml.Response()
		resp.say(return_value, voice="alice", language="en-CA")

		return str(resp)
	# if caller presses anything else or call fails
	else:
		resp.say("The call failed, or the remote party hung up. Goodbye.", voice="alice", language="en-CA")
		return redirect("/")


@app.route("/app/", methods=['GET', 'POST'])
def callRoute(failedCall=False):
  resp = twilio.twiml.Response()
  form = MySite(request.form, failedCall=failedCall, csrf_enabled = False)
  if form.validate_on_submit():
      return make_call(form.data['phoneNumber'])
  return render_template('mysite.html',
        title = 'Enter A Phone Number starting with country code +1',
        form = form)

if __name__ == "__main__":
	app.run(debug=True)


