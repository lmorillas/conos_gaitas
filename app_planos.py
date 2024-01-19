import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import hmac
from csv import DictReader

df = px.data.gapminder()

fig = px.scatter(
    df.query("year==2007"),
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    size_max=60,
)

# Funciones auxiliares para el digujo
def punto(x):
    return x.replace(',', '.')

def procesa_asiento(lista, long_total):
    return [(float(punto(x.get('diametro_asiento')))/2, 
            long_total - float(punto(x.get('long_asiento')))) for x in lista]

def procesa_cono(lista, long_total):
    return [(float(punto(x.get('diametro_cono')))/2, 
            float(punto(x.get('long_cono')))) for x in lista]

def grafica_de_csv(fcsv="", color="", label=""):
    #hoja = DictReader(open(fcsv))
    if not fcsv:
        cono = st.secrets["conos"]["bestue"]
        hoja = DictReader(cono.splitlines())
    else:
        hoja = DictReader(open(fcsv))
    datos = [a for a in hoja]
    nombre = [m.get('nombre') for m in datos if m.get('nombre')][0]

    long_total = float([m.get('total') for m in datos if m.get('total')][0].replace(',', '.'))
    garganta = float([m.get('garganta') for m in datos if m.get('garganta')][0].replace(',', '.'))/2

    asiento_ = [m for m in datos if m.get('diametro_asiento') and m.get('long_asiento')]
    asiento = procesa_asiento(asiento_, long_total)
    

    cono_ = [m for m in datos if m.get('diametro_cono') and m.get('long_cono')]
    cono = procesa_cono(cono_, long_total)
    ultiasiento = asiento[-1][1]
    primecono = cono[0][1]
    mitad = (ultiasiento-primecono) / 2
    #print(asiento)
    asiento.append((garganta, ultiasiento - mitad))
    #print(asiento)

    clarin = asiento + cono
    #print(clarin)
    y = [x[1] for x in clarin]
    y_ = [x[1] for x in clarin]
    y_.reverse()
    x = [x[0]for x in clarin]
    x_ = [-x[0] for x in clarin]
    x_.reverse()
    x = x + x_
    y = y + y_

    return {'nombre': nombre,
            'x': x,
            'y': y}


def panel():
    st.sidebar.title("Panel de selección")
    st.sidebar.selectbox("Gaita", ["Bestué", "Robres", "Santa Justa"])
    

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

    

def main():
    if not check_password():
        st.stop()  # Do not continue if check_password is not True.
    panel()
    puntero = grafica_de_csv() # '', 'blue', 'Bestué')
    altura = st.sidebar.slider('Altura del gráfico', 200, 1200, 600)
    anchura = st.sidebar.slider('Anchura del gráfico', 5, 40, int(max(puntero['x'])+1))  
    altura_punt = int(max(puntero['y']))  
    
    st.title("Análisis de conos de gaitas antiguas")
    st.subheader("Pablo Carpintero")
    
    #st.write(puntero)
    fig = px.line(puntero, x="x", y="y", 
                title='Gaita de Bestué', height=altura,
                )
    
    fig.update_layout(xaxis_range=[-1 * anchura,anchura])
    

    st.plotly_chart(fig, theme="streamlit", use_container_width=False)

    figa = go.Figure()
    figa.add_trace(go.Scatter(x=puntero['x'], y=puntero['y'],
        fill='tozerox',
        mode='lines',
        line_color='yellow',
        ),

    )
    figa.update_layout(xaxis_range=[-1 * anchura,anchura], 
                       yaxis_range=[0 , altura_punt + 30],
                       height=altura)
    
    st.write('Relleno')
    st.plotly_chart(figa, theme="streamlit", use_container_width=True)

if __name__ == "__main__":
    main()
