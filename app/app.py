from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from sqlalchemy import or_

app = Flask(__name__)

app.config.from_object(Config)

mododebug = True

db = SQLAlchemy(app)

class Matriculas(db.Model):
    id_matriculas = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    curso = db.Column(db.String(100), nullable=False)
    cadastrado = db.Column(db.Integer, nullable=False)
    uidnumber = db.Column(db.Integer, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    # Obtém o número da página atual a partir do parâmetro da URL 'page'
    page = request.args.get('page', 1, type=int)
    # Define o número de itens por página
    per_page = 6

    if request.method == 'POST':
        # Obter a entrada do usuário a partir do formulário de pesquisa
        search_term = request.form.get('search')
        # Consultar o banco de dados para encontrar matrículas correspondentes ao termo de pesquisa
        matriculas = Matriculas.query.filter(or_(Matriculas.nome.like(f'%{search_term}%'), Matriculas.matricula.like(f'%{search_term}%')))\
            .order_by(Matriculas.id_matriculas.desc()).paginate(page=page, per_page=per_page)
        return render_template('index.html', matriculas=matriculas, search=search_term)
    else:
        # Se nenhum termo de pesquisa foi fornecido, retornar todas as matrículas
        matriculas = Matriculas.query.order_by(Matriculas.id_matriculas.desc()).paginate(page=page, per_page=per_page)

        return render_template('index.html', matriculas=matriculas)

@app.route('/add', methods=['POST'])
def add_matricula():
    matricula = request.form.get('matricula')
    nome = request.form.get('nome', '').upper()
    curso = request.form.get('curso', '').upper()

    if not matricula:
        flash('A matricula é obrigatória.', 'error')
        return redirect(url_for('index'))

    matricula_obj = Matriculas.query.filter_by(matricula=matricula).first()
    if matricula_obj:
        flash(f"A matricula {matricula} já esta cadastrada.", 'error')
        return redirect(url_for('index'))

    uidnumber = get_next_uidnumber()

    matricula_obj = Matriculas(
        matricula=matricula, nome=nome, curso=curso, 
        cadastrado=0, uidnumber=uidnumber
    )
    db.session.add(matricula_obj)
    db.session.commit()
    flash(f"A matricula {matricula} foi cadastrada com sucesso.", 'success')
    return redirect(url_for('index'))

def get_next_uidnumber():
    last_uidnumber = Matriculas.query.order_by(Matriculas.id_matriculas.desc()).first().uidnumber
    return int(last_uidnumber) + 1


@app.route('/update/<id>', methods=['POST'])
def update_matricula(id):
    matricula_id = id
    matricula = Matriculas.query.get(matricula_id)
    matricula.matricula = request.form['matricula']
    matricula.nome = request.form['nome'].upper()
    matricula.curso = request.form['curso'].upper()
    matricula.cadastrado = request.form['cadastrado']
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<id>', methods=['GET'])
def delete_matricula(id):
    matricula = Matriculas.query.get(id)
    db.session.delete(matricula)
    db.session.commit()
    flash(f"A matrícula: {matricula.matricula} foi excluída com sucesso.", 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if mododebug:
        # Rodar modo Debug
        app.run(debug=True)
    else:
        # Executar modo produção
        print("Escutando na porta 5000")
        serve(app, host="0.0.0.0", port=5000)
