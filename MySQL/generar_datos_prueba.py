"""Genera personas e investigaciones FICTICIAS para el entorno local.

    env\\Scripts\\python.exe MySQL/generar_datos_prueba.py
    env\\Scripts\\python.exe MySQL/generar_datos_prueba.py --limpiar

Ninguno de estos datos corresponde a una persona real. Las CURP y los RFC
tienen formato valido pero se construyen con nombres inventados, asi que no
identifican a nadie. No ejecutar nunca contra la base de produccion.
"""
import os
import sys
import random
import json
from datetime import date, timedelta

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LegalBit.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from Personas.models import Personas
from Investigaciones.models import Investigacion
from Generales.models import Estados, Municipios, Colonia, EstadosCiviles, LugarNacimientoCURP

# Nombres deliberadamente comunes, combinados al azar: no aluden a nadie.
NOMBRES_H = ['MIGUEL', 'JORGE', 'ANDRES', 'RICARDO', 'FERNANDO', 'JAVIER',
             'ALEJANDRO', 'RAUL', 'ARTURO', 'SERGIO', 'PABLO', 'EMILIO']
NOMBRES_M = ['LUCIA', 'MARIANA', 'PATRICIA', 'ADRIANA', 'VERONICA', 'CLAUDIA',
             'ELENA', 'ROSARIO', 'BEATRIZ', 'SILVIA', 'CAROLINA', 'TERESA']
APELLIDOS = ['RAMIREZ', 'SALAZAR', 'MENDOZA', 'CASTILLO', 'HERRERA', 'VARGAS',
             'ESCOBAR', 'PINEDA', 'ZAMORA', 'QUINTERO', 'BELTRAN', 'ARELLANO',
             'CARRILLO', 'MONTES', 'IBARRA', 'GALVAN', 'ROSALES', 'TAPIA']

VOCALES = 'AEIOU'
CONSONANTES = 'BCDFGHJKLMNPQRSTVWXYZ'


def _primera_vocal_interna(palabra):
    for c in palabra[1:]:
        if c in VOCALES:
            return c
    return 'X'


def _primera_consonante_interna(palabra):
    for c in palabra[1:]:
        if c in CONSONANTES:
            return c
    return 'X'


def construir_curp(nombre, ap1, ap2, fnac, sexo, clave_entidad):
    """CURP con la estructura oficial, a partir de datos inventados."""
    base = (ap1[0] + _primera_vocal_interna(ap1) + ap2[0] + nombre[0]).upper()
    fecha = fnac.strftime('%y%m%d')
    consonantes = (_primera_consonante_interna(ap1) +
                   _primera_consonante_interna(ap2) +
                   _primera_consonante_interna(nombre)).upper()
    homoclave = random.choice('0123456789') + random.choice('0123456789')
    return f'{base}{fecha}{sexo}{clave_entidad}{consonantes}{homoclave}'


def construir_rfc(nombre, ap1, ap2, fnac):
    base = (ap1[:2] + ap2[0] + nombre[0]).upper()
    fecha = fnac.strftime('%y%m%d')
    homoclave = ''.join(random.choice('ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789')
                        for _ in range(3))
    return f'{base}{fecha}{homoclave}'


def _burojson_falso(nombre, ap1):
    """Estructura equivalente a la que devuelve Moffin, con cifras inventadas."""
    return json.dumps({
        'response': {'json': {
            'score': {'value': random.randint(500, 820)},
            'persona': {'nombre': nombre, 'apellidoPaterno': ap1},
            'creditos': [{
                'institucion': random.choice(['BANORTE', 'BBVA', 'SANTANDER', 'HSBC']),
                'saldoActual': random.randint(0, 250000),
                'limiteCredito': random.randint(10000, 400000),
                'formaPago': random.choice(['01', '01', '01', '02', '03']),
            } for _ in range(random.randint(1, 4))],
        }},
        '_ficticio': True,
    }, ensure_ascii=False)


def _antecedentesjson_falso():
    """La mayoria sin antecedentes, algunos con expedientes inventados."""
    if random.random() < 0.7:
        return json.dumps({'code': 999, 'data': {'resultados': []},
                           '_ficticio': True}, ensure_ascii=False)
    return json.dumps({
        'code': 200,
        'data': {'resultados': [{
            'entidad': random.choice(['YUCATAN', 'NUEVO LEON', 'CAMPECHE']),
            'expedientes': [{
                'actor': 'PARTE ACTORA FICTICIA',
                'demandado': 'PARTE DEMANDADA FICTICIA',
                'materia': random.choice(['CIVIL', 'MERCANTIL', 'FAMILIAR']),
                'expediente': f'{random.randint(100, 999)}/{random.randint(2018, 2025)}',
            }],
        }]},
        '_ficticio': True,
    }, ensure_ascii=False)


def limpiar(usuario):
    n_inv = Investigacion.objects.filter(usuario=usuario).count()
    n_per = Personas.objects.filter(usuario=usuario).count()
    Investigacion.objects.filter(usuario=usuario).delete()
    Personas.objects.filter(usuario=usuario).delete()
    print(f'Borradas {n_inv} investigaciones y {n_per} personas de "{usuario.username}".')


def main():
    if connection.settings_dict['HOST'] not in ('127.0.0.1', 'localhost', ''):
        sys.exit(f'ABORTADO: la base apunta a {connection.settings_dict["HOST"]}, '
                 'no a tu maquina. Este script es solo para local.')

    usuario = User.objects.filter(username='admin').first()
    if not usuario:
        sys.exit('No existe el usuario "admin". Crealo primero.')

    if '--limpiar' in sys.argv:
        limpiar(usuario)
        return

    estados = list(Estados.objects.all())
    municipios = list(Municipios.objects.all())
    colonias = list(Colonia.objects.all())
    civiles = list(EstadosCiviles.objects.all())
    lugares = list(LugarNacimientoCURP.objects.all())
    if not (estados and municipios and colonias and civiles and lugares):
        sys.exit('Faltan catalogos. Carga primero MySQL/catalogos.sql')

    creadas = []
    for _ in range(50):
        sexo = random.choice('HM')
        nombre = random.choice(NOMBRES_H if sexo == 'H' else NOMBRES_M)
        ap1, ap2 = random.sample(APELLIDOS, 2)
        fnac = date(1960, 1, 1) + timedelta(days=random.randint(0, 16000))
        lugar = random.choice(lugares)
        municipio = random.choice(municipios)
        colonia = random.choice([c for c in colonias
                                 if c.municipio_id == municipio.id] or colonias)

        p = Personas.objects.create(
            nombre=nombre, apellido1=ap1, apellido2=ap2,
            razonsocial=f'{nombre} {ap1} {ap2}',
            curp=construir_curp(nombre, ap1, ap2, fnac, sexo, lugar.clave),
            rfc=construir_rfc(nombre, ap1, ap2, fnac),
            fnacimiento=fnac,
            correo_electronico=f'{nombre.lower()}.{ap1.lower()}@ejemplo-ficticio.mx',
            telefono_principal=f'999{random.randint(1000000, 9999999)}',
            telefono_secundario='',
            calle=f'CALLE {random.randint(1, 80)}',
            numExterior=str(random.randint(100, 999)),
            estadocivil=random.choice(civiles),
            lugarNacimiento=lugar,
            estado=random.choice(estados),
            municipio=municipio,
            colonia=colonia,
            tipo='PF', manual=True,
            validaine='ND', clave_elector='ND', cic_ine='ND', identificador_ine='ND',
            uuid_imss='NA', uuid_issste='NA',
            usuario=usuario,
        )
        creadas.append(p)

    folio = 1000
    for p in random.sample(creadas, 30):
        folio += 1
        Investigacion.objects.create(
            investigado=p,
            usuario=usuario,
            folio=folio,
            nombre_archivo='ND',
            aprobado=True,
            burojson=_burojson_falso(p.nombre, p.apellido1),
            antecedentesjson=_antecedentesjson_falso(),
            estudiosprofesionalesjson='ND',
            listanegraintl='ND',
            satblacklistjson='ND',
            notas='DATOS FICTICIOS - generados para pruebas locales',
        )

    print(f'Listo: {len(creadas)} personas y 30 investigaciones ficticias.')
    print(f'Total en la base: {Personas.objects.count()} personas, '
          f'{Investigacion.objects.count()} investigaciones.')


if __name__ == '__main__':
    main()
