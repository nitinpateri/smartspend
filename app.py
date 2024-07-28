import flask
import pickle 
app = flask.Flask(__name__)

#Index Page
@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/register')
def register():
    return flask.render_template('register.html')

#login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
            global email1
            global passwd
            passwd = flask.request.form['password']
            email1 = flask.request.form['email']
            global user_login
            try:
                user_login = open('user_data.dat','rb')
                load = pickle.load(user_login)
                for i in load:
                    if i == email1:
                        if load[i]['password'] == passwd:
                            return flask.redirect(email1+'/home')
                        else:
                            return flask.render_template('index.html',data=2)
            except:
                return flask.render_template('index.html',data=4)
            return flask.render_template('index.html',data=3)
    
#Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.request.method == 'POST':
        try:
            user_login = open('user_data.dat','rb')
            load = pickle.load(user_login)
            if flask.request.form['email'] in load:
                    return flask.render_template('register.html',data=0)
            print(1)
            temp=1
            user_login.close()
        except: 
            if flask.request.form['email'] in load:
                    return flask.render_template('register.html',data=0)
            temp=0
        
        file = open('user_data.dat','wb')
        if temp==0:
            user_data = {flask.request.form['email']:{
            "password": flask.request.form['password']
            }}
            pickle.dump(user_data,file)
            file.close()
        else:
            load[flask.request.form['email']]={
            "password": flask.request.form['password']
            }
            pickle.dump(load,file)
            file.close()
        return flask.redirect('/')

@app.route('/profile')
def profile():
    return flask.render_template('profile.html')

@app.route('/display')
def display():
    return flask.render_template('display.html')

@app.route('/<id>/home')
def home(id):
    file = open('user_data.dat','rb')
    load = pickle.load(file)
    if id in load:
        return flask.render_template('home.html',data=[id])
    else:
        return flask.render_template('404Error.html')
    
@app.route('/<id>/expense-tracker')
def expense_tracker(id):
    file = open('user_data.dat','rb')
    load = pickle.load(file)
    if id in load:
        return flask.render_template('expense_tracker.html',data=[id])
    else:
        return flask.render_template('404Error.html')
    

@app.route('/<id>/financial-calculators')
def fc(id):
    file = open('user_data.dat','rb')
    load = pickle.load(file)
    if id in load:
        return flask.render_template('finanial_cal.html',data=[id])
    else:
        return flask.render_template('404Error.html')

@app.route('/<id>/daily',methods=['GET', 'POST'])
def daily(id):
    if flask.request.method == 'POST':
        file = open('user_data.dat','rb')
        load = pickle.load(file)
        if id in load:
            purpose=flask.request.form['purpose']
            date=flask.request.form['date']
            amount=flask.request.form['amount']
            if 'expense_tracker' in load[id]:
                load[id]['expense_tracker'].append([date,purpose,amount])
            else:
                load[id]['expense_tracker']=[[date,purpose,amount]]
            file.close()
            file = open('user_data.dat','wb')
            pickle.dump(load,file)
            file.close()
            return flask.render_template('daily.html')
    file = open('user_data.dat','rb')
    load = pickle.load(file)
    if id in load:
        return flask.render_template('daily.html',data=[id])

@app.route('/<id>/monthly',methods=['GET', 'POST'])
def monthly(id):
    file = open('user_data.dat','rb')
    load = pickle.load(file)
    if id in load:
        load = load[id]['expense_tracker']
        total=0
        for i in load:
            total+=int(i[2])
        chart_values=[]
        for i in load:
            chart_values.append((int(i[2])//total)*100)
        return flask.render_template('monthly.html',data=[load,total,chart_values,id])
    return flask.render_template('404.html')

@app.route('/<id>/tax-cal',methods=['GET', 'POST'])
def tax_cal(id):
    if flask.request.method == "POST":
        income =  int(flask.request.form['income'])
        t_income=income
        deduction =  flask.request.form.getlist('deduction')
        sum1=0
        for i in deduction[:10]:
            sum1+=int(i)
        if sum1>=150000:
            income-=150000
            sum1=150000
        else:
            income-=sum1
        if int(deduction[10]) >=50000:
            income-=50000
            sum1+=50000
        else:
            income-=int(deduction[10])
            sum1+=int(deduction[10])
        if int(deduction[13]) >=150000:
            income-=150000
            sum1+=150000
        else:
            income-=int(deduction[13])
            sum1+=int(deduction[13])
        if int(deduction[-5]) >=200000:
            income-=200000
            sum1+=200000
        else:
            income-=int(deduction[-5])
            sum1+=int(deduction[-5])
        if income <= 300000:
            tax = 0
        elif income <= 600000:
            tax = (income - 300000) * 0.05
        elif income <= 900000:
            tax = (income - 600000) * 0.1 + 300000 * 0.05
        elif income <= 1200000:
            tax = (income - 900000) * 0.15 + 300000 * 0.1 + 300000 * 0.05
        elif income <= 1500000:
            tax = (income - 1200000) * 0.2 + 300000 * 0.15 + 300000 * 0.1 + 300000 * 0.05
        else:
            tax = (income - 1500000) * 0.3 + 300000 * 0.2 + 300000 * 0.15 + 300000 * 0.1 + 300000 * 0.05
        tax = tax + tax * 0.04
        return flask.render_template('tax_output.html',data=[t_income,tax,income,sum1,1])
    return flask.render_template('tax.html',data=[0])

def calculate_home_loan_emi(loan_amount, annual_interest_rate, tenure_years):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    total_months = tenure_years * 12
    EMI = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** total_months) / ((1 + monthly_interest_rate) ** total_months - 1)
    return EMI

def calculate_total_liquid_assets(cash, bonds, gold, mutual_funds, stocks):
    return cash + bonds + gold + mutual_funds + stocks

@app.route('/<id>/affordability-cal', methods=['GET', 'POST'])
def home_loan(id):
    if flask.request.method == 'POST':
        data = {
            'cost_of_property': float(flask.request.form['cost_of_property']),
            'down_payment': float(flask.request.form['down_payment']),
            'loan_amount': float(flask.request.form['loan_amount']),
            'annual_interest_rate': float(flask.request.form['annual_interest_rate']),
            'tenure_years': int(flask.request.form['tenure_years']),
            'cost_of_registration': float(flask.request.form['cost_of_registration']),
            'cash_in_bank_accounts': float(flask.request.form['cash_in_bank_accounts']),
            'bonds': float(flask.request.form['bonds']),
            'gold': float(flask.request.form['gold']),
            'mutual_funds': float(flask.request.form['mutual_funds']),
            'stocks': float(flask.request.form['stocks'])
        }
        
        data['EMI'] = calculate_home_loan_emi(data['loan_amount'], data['annual_interest_rate'], data['tenure_years'])
        data['total_liquid_assets'] = calculate_total_liquid_assets(data['cash_in_bank_accounts'], data['bonds'], data['gold'], data['mutual_funds'], data['stocks'])
        
        return flask.render_template('home_loanoutput.html', data=data)
    
    return flask.render_template('home_loan.html')

# SIP calculator
def calculate_total_expenses(housing, transportation, utilities, groceries, medical, dining, shopping, insurance_premiums, child_education, maid, miscellaneous, home_loan, car_loan, personal_loan, other_loans):
    total_living_expense = housing + transportation + utilities + groceries + medical
    total_lifestyle_expense = dining + shopping
    total_other_expenses = insurance_premiums + child_education + maid + miscellaneous
    total_emis = home_loan + car_loan + personal_loan + other_loans
    total_expenses = total_living_expense + total_lifestyle_expense + total_other_expenses + total_emis
    return total_expenses, total_living_expense, total_lifestyle_expense, total_other_expenses, total_emis

def calculate_savings(total_income, total_expenses):
    return total_income - total_expenses

def calculate_sip(corpus_goal, annual_return_rate, investment_period_months):
    monthly_return_rate = (1 + annual_return_rate) ** (1 / 12) - 1
    sip = corpus_goal * monthly_return_rate / (((1 + monthly_return_rate) ** investment_period_months - 1) / monthly_return_rate)
    return sip

def calculate_corpus(sip, annual_return_rate, investment_period_months):
    monthly_return_rate = (1 + annual_return_rate) ** (1 / 12) - 1
    corpus = sip * (((1 + monthly_return_rate) ** investment_period_months - 1) / monthly_return_rate) * (1 + monthly_return_rate)
    return corpus

@app.route('/<id>/sip-calculator', methods=['GET', 'POST'])
def sip(id):
    if flask.request.method == 'POST':
        data = {
            'sip_amount': float(flask.request.form['sip_amount']),
            'investment_period_months': int(flask.request.form['investment_period_months']),
            'annual_return_rate': float(flask.request.form['annual_return_rate'])
        }

        corpus = calculate_corpus(data['sip_amount'], data['annual_return_rate'], data['investment_period_months'])
        data['corpus'] = corpus
        
        return flask.render_template('sip_output.html', data=data)
    
    return flask.render_template('sip_calculator.html')

def calculate_future_values(present_age, current_cost, inflation_rate, goal_age, roi, initial_lump_sum):
    years_to_goal = goal_age - present_age
    future_cost = current_cost * (1 + inflation_rate / 100) ** years_to_goal

    if initial_lump_sum > 0:
        corpus_required = future_cost - initial_lump_sum * (1 + roi / 100) ** years_to_goal
    else:
        corpus_required = future_cost

    if corpus_required < 0:
        corpus_required = 0

    monthly_investment = corpus_required / ((1 + roi / 100 / 12) ** (years_to_goal * 12) - 1) * (roi / 100 / 12)
    annual_investment = monthly_investment * 12
    lump_sum_investment = corpus_required / (1 + roi / 100) ** years_to_goal

    return {
        'corpus_required': round(corpus_required, 2),
        'monthly_investment': round(monthly_investment, 2),
        'annual_investment': round(annual_investment, 2),
        'lump_sum_investment': round(lump_sum_investment, 2)
    }


@app.route('/<id>/children-future', methods=['GET', 'POST'])
def children_future(id):
    if flask.request.method == 'POST':
        data = {
            'present_age': int(flask.request.form['present_age']),
            'current_cost': float(flask.request.form['current_cost']),
            'inflation_rate': float(flask.request.form['inflation_rate']),
            'goal_age': int(flask.request.form['goal_age']),
            'roi': float(flask.request.form['roi']),
            'initial_lump_sum': float(flask.request.form.get('initial_lump_sum', 0))
        }

        results = calculate_future_values(
            data['present_age'],
            data['current_cost'],
            data['inflation_rate'],
            data['goal_age'],
            data['roi'],
            data['initial_lump_sum']
        )

        return flask.render_template('children_fut_op.html', data=results)

    return flask.render_template('children_fut.html')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8000', debug='True')