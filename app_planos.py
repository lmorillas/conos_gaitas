import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import hmac
import folium
from streamlit_folium import st_folium
from csv import DictReader

# Funciones auxiliares para el digujo
def punto(x):
    return x.replace(',', '.')

def procesa_asiento(lista, long_total):
    return [(float(punto(x.get('diametro_asiento')))/2, 
            long_total - float(punto(x.get('long_asiento')))) for x in lista]

def procesa_cono(lista, long_total):
    return [(float(punto(x.get('diametro_cono')))/2, 
            float(punto(x.get('long_cono')))) for x in lista]

def grafica_de_csv(cono):
    #hoja = DictReader(open(fcsv))
    hoja = DictReader(cono.splitlines())
    
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
    coord_origen = [m.get('coord_origen') for m in datos if m.get('coord_origen')][0]
    coord_medicion = [m.get('coord_medicion') for m in datos if m.get('coord_medicion')][0]
    lugar_origen = [m.get('lugar_origen') for m in datos if m.get('lugar_origen')][0]
    lugar_medicion = [m.get('lugar_medicion') for m in datos if m.get('lugar_medicion')][0]
    return {'nombre': nombre,
            'x': x,
            'y': y,
            'coord_origen': [float(x) for x in coord_origen.split(',')],
            'coord_medicion': [float(x) for x in coord_medicion.split(',')],
            'lugar_origen': lugar_origen,
            'lugar_medicion': lugar_medicion
            }


def panel():
    st.sidebar.title("Panel de selección")
    
    

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

    
def mapa(puntero: dict):
    # create a Folium Map object
    m = folium.Map(location=puntero.get('coord_medicion'), zoom_start=10,
                   tiles="Stamen Terrain",
                    attr='Map data © OpenStreetMap contributors, CC-BY-SA, Imagery © Mapbox')
    
    kw1 = { "color": "green", "icon": "home"}
    kw2= { "color": "blue", "icon": "pencil"}
    icon1 = folium.Icon( **kw1)
    icon2 = folium.Icon( **kw2)
    folium.Marker(
        puntero.get('coord_origen'), popup=puntero.get('lugar_origen'), 
        tooltip=puntero.get('lugar_origen'), icon=icon1
    ).add_to(m)
    folium.Marker(
        puntero.get('coord_medicion'), popup=puntero.get('lugar_medicion'), 
        tooltip=puntero.get('lugar_medicion'), icon = icon2
    ).add_to(m)

    # call to render Folium map in Streamlit
    st_folium(m, width=725,  returned_objects=[])


#@st.cache
def carga_datos():
    datos = st.secrets["conos"]
    conos = [k for k in datos.keys()]
    conos_dict = {k: grafica_de_csv(datos[k]) for k in conos}
    return conos_dict

def main():
    # if not check_password():
    #     st.stop()  # Do not continue if check_password is not True.
    panel()

    mis_conos = carga_datos()
    nombres = {mis_conos[k]['nombre']:k for k in mis_conos.keys()}
    cono_sel = st.sidebar.selectbox("Gaita", sorted(list(nombres)),
                                    index=0, 
                                    key="cono", placeholder="Selecciona una gaita")    
    

    #st.write(cono_sel)
    cono_sel = nombres[cono_sel]
    

    puntero = mis_conos[cono_sel] # '', 'blue', 'Bestué')
    cono={}
    cono['x'] = puntero['x']
    cono['y'] = puntero['y']
    altura = st.sidebar.slider('Altura del gráfico', 200, 1200, 600)
    anchura = st.sidebar.slider('Anchura del gráfico', 5, 100, int(max(cono['x'])+1))  
    altura_punt = int(max(cono['y']))  
    
    st.sidebar.divider()
            
    st.title("Análisis de conos de gaitas antiguas")
    st.subheader("Pablo Carpintero")
    st.divider()
    st.subheader(puntero['nombre'])
    tab1, tab2 = st.tabs(["Conos", "Info"])
    with tab1:
        st.markdown("""[Cono línea](#línea)   ::    [Cono área](#área) :: [Mapa](#mapa)""",  unsafe_allow_html=True)
        st.subheader("Cono línea", anchor="línea")
        fig = px.line(cono, x="x", y="y", 
                    #title=puntero['nombre'],
                    height=altura,
                    )
        
        fig.update_layout(xaxis_range=[-1 * anchura,anchura])
        

        st.plotly_chart(fig, theme="streamlit", use_container_width=False)

        st.subheader("Cono área", anchor="área")
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

        st.subheader("Mapa origen y medición", anchor="mapa")
        mapa( puntero )
    with tab2:
        st.subheader("Datos de medición", anchor="datos")
        st.markdown("""
        * lugar de medición, 
        * fecha,
        * fotos
        * medidas
        * grabaciones
        * etc
        """)
    

if __name__ == "__main__":
    main()
