const asideControl = document.getElementById("aside-control")
const menuMobile = document.getElementById("mobile-button")
const menuMobile2 = document.getElementById("mobile-button2")
const aside = document.getElementById("aside");

asideControl.addEventListener("click", e => {
    const textLinks = document.getElementsByClassName("text-link");
    const iconControl = document.getElementById("icon-control");
    iconControl.classList.toggle("fa-chevron-right")
    iconControl.classList.toggle("fa-chevron-left")
    for (let i = 0; i < textLinks.length; i++) {
        textLinks[i].classList.toggle("hidden");
    }
    aside.classList.toggle("collapsed")
});

function alternar_estado(id) {
    let input = document.getElementById(id);
    if (input.disabled) {
        input.disabled = false;
        if (id == "id_fecha_nacimiento") {
            input.type = "date"
        }
        // Establecer el foco al final del valor existente
        input.setSelectionRange(input.value.length, input.value.length);
        input.focus();
    } else {
        input.disabled = true
        if (id == "id_fecha_nacimiento") {
            input.type = "text"
        }
    }
}

menuMobile.addEventListener("click", e => {
    aside.classList.toggle("show")
});

menuMobile2.addEventListener("click", e => {
    aside.classList.toggle("show")
});

function calcular_dv(id) {
    // Obtén el valor actual del campo de entrada
    const inputElement = document.getElementById(id)
    const inputValue = inputElement.value;

    // Aplica una expresión regular para mantener solo los dígitos permitidos
    const sanitizedValue = inputValue.replace(/[^0-9]/g, '');

    // Limita la longitud del valor a 9 caracteres
    const limitedValue = sanitizedValue.slice(0, 8);

    // Formatea el valor con puntos cada tres dígitos
    const formattedValue = limitedValue.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    // Actualiza el valor del campo de entrada con el formato deseado
    inputElement.value = formattedValue;

    // Extraer el valor sin puntos
    const extractedValue = inputElement.value.replace(/\./g, '');

    //Actualizar el valor del campo DV
    document.getElementById("dv").value = dgv(extractedValue)
};

function dgv(T) {
    var M = 0, S = 1;
    for (; T; T = Math.floor(T / 10))
        S = (S + T % 10 * (9 - M++ % 6)) % 11;
    return S ? S - 1 : 'K';
}

function convertir_tipo(id, tipo) {
    const elment = document.getElementById(id);
    elment.type = tipo;
}




function generarCadenaAleatoria(longitud) {
    const caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let cadenaAleatoria = '';

    for (let i = 0; i < longitud; i++) {
        const caracterAleatorio = caracteres.charAt(Math.floor(Math.random() * caracteres.length));
        cadenaAleatoria += caracterAleatorio;
    }

    return cadenaAleatoria;
};

function guardar_usuario() {
    const password = generarCadenaAleatoria(8)
    document.getElementById("id_password1").value = password
    document.getElementById("id_password2").value = password
    document.getElementById("form_usuario").submit()
};

function expand_profile() {
    const profile = document.getElementById("profile-menu")
    profile.hidden = !profile.hidden
    document.getElementById("profile-icon").classList.toggle("fa-chevron-right")
    document.getElementById("profile-icon").classList.toggle("fa-chevron-left")
}

function expand_usuarios() {
    const usuarios = document.getElementById("usuarios-list")
    usuarios.hidden = !usuarios.hidden
    document.getElementById("usuarios-icon").classList.toggle("fa-chevron-down")
    document.getElementById("usuarios-icon").classList.toggle("fa-chevron-up")
    tutorial2()
}

const listaUsuariosIngresados = document.getElementById("usuarios-list")


function get_loggin() {
    fetch("/usuarios/logged/")
        .then(response => response.json())
        .then(data => {
            listaUsuariosIngresados.innerHTML = ""
            for (let i = 0; i < data.length; i++) {
                listaUsuariosIngresados.innerHTML += data[i] + "<br>"
            }
        })
}
setInterval(get_loggin, 30000);

get_loggin()

function validar_fecha(input) {
    const fecha = input.value.split("-")
    const fecha_actual = new Date()

    const fecha_ingresada = new Date(fecha[0], fecha[1] - 1, fecha[2])

    if (fecha_actual > fecha_ingresada) {
        input.value = ""
        document.getElementById("fecha_alert").innerHTML = "La fecha no puede ser menor a la actual"
    } else {
        document.getElementById("fecha_alert").innerHTML = ""
    }
}

function validar_fecha_menor(input) {
    const elemento = document.getElementById(input)
    const fecha = elemento.value.split("-")
    const fecha_actual = new Date()

    const fecha_ingresada = new Date(fecha[0], fecha[1] - 1, fecha[2])

    if (fecha_actual < fecha_ingresada) {
        elemento.value = ""
        document.getElementById("fecha_alert").innerHTML = "La fecha no puede ser mayor a la actual"
    } else {
        document.getElementById("fecha_alert").innerHTML = ""
    }
}



function validar_fecha_hora(input) {
    const element = document.getElementById(input)
    const fecha = element.value.split("T")[0]
    const hora = element.value.split("T")[1]
    const fecha_actual = new Date()
    const fecha_ingresada = new Date(fecha.split("-")[0], fecha.split("-")[1] - 1, fecha.split("-")[2], hora.split(":")[0], hora.split(":")[1])

    if (fecha_actual > fecha_ingresada) {
        element.value = ""
        document.getElementById("fecha_alert").innerHTML = "La fecha no puede ser menor a la actual"
        element.style.borderBottom = "1px solid red"
    } else {
        document.getElementById("fecha_alert").innerHTML = ""
        element.style.borderBottom = "1px solid #1e1e1e"
    }

}

function validar_fecha_hora_termino(input) {
    const element = document.getElementById(input)
    const fecha = element.value.split("T")[0]
    const hora = element.value.split("T")[1]
    const fecha_inicio = document.getElementById("id_fecha_inicio").value.split("T")[0]
    const hora_inicio = document.getElementById("id_fecha_inicio").value.split("T")[1]
    const fecha_actual = new Date(fecha_inicio.split("-")[0], fecha_inicio.split("-")[1] - 1, fecha_inicio.split("-")[2], hora_inicio.split(":")[0], hora_inicio.split(":")[1])
    const fecha_ingresada = new Date(fecha.split("-")[0], fecha.split("-")[1] - 1, fecha.split("-")[2], hora.split(":")[0], hora.split(":")[1])

    if (fecha_actual > fecha_ingresada) {
        element.value = ""
        document.getElementById("fecha_alert").innerHTML = "La fecha de término no puede ser menor a la fecha de inicio"
        element.style.borderBottom = "1px solid red"
    } else {
        document.getElementById("fecha_alert").innerHTML = ""
        element.style.borderBottom = "1px solid #1e1e1e"
    }
}


function validar_positivo(input) {
    if (input.value < 0) {
        input.value = 0
        document.getElementById("positive_alert").innerHTML = "El valor no puede ser negativo"
    } else {
        document.getElementById("positive_alert").innerHTML = ""
    }
}



function tutorial_evento() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('.fc-toolbar-chunk:nth-child(2)'),
                intro: 'Este es el calendario, aquí podrás ver todos los eventos que tienes agendados',

            },
            {
                element: document.querySelector('.fc-toolbar'),
                intro: 'Este es el menú de opciones, aquí podrás ver los eventos de la semana, mes o día, y ver los eventos de todos los usuarios',

            },
            {
                element: document.querySelector('#btn-agregar-evento'),
                intro: 'Este es el botón para agregar un evento, puedes agregar un evento en el día que quieras',

            },
            {
                element: document.querySelector('#lista_espera'),
                intro: 'Esta es la lista de espera, aquí se mostraran los pacientes que esperan ser atendidos',

            },
            {
                element: document.querySelector('#myChart'),
                intro: 'Aqui se muestra la cantidad de pacientes que han sido atendidos cada mes',
                
            }

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}

function tutorial_usuario() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('#wrapper'),
                intro: 'Esta es la lista de usuarios que han ingresado al sistema',

            },
            {
                element: document.querySelector('#btn-agregar-usuario'),
                intro: 'Este es el botón para agregar un usuario, puedes agregar un usuario con el rol que quieras',

            },
            {
                element: document.querySelector('[data-column-id="acciones"]'),
                intro: 'Acá puedes ver las acciones que puedes realizar con cada usuario, Como editar o bloquear',
            },
            

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}

function tutorial_paciente() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('#wrapper'),
                intro: 'Esta es la lista de pacientes que han ingresado al sistema',

            },
            {
                element: document.querySelector('#btn-agregar-paciente'),
                intro: 'Este es el botón para agregar un paciente',

            },
            {
                element: document.querySelector('[data-column-id="perfil"]'),
                intro: 'Acá puedes ver el perfil de cada paciente, y editar sus datos',
            },
            

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}

function tutorial_perfil_paciente() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('#perfil-paciente'),
                intro: 'Aquí puedes ver los datos del paciente y editarlos.',

            },
            {
                element: document.querySelector('#perfil-historial'),
                intro: 'Aquí puedes ver el historial de atenciones del paciente, y agregar nuevas solicitudes.',

            },

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}

function tutorial_insumo() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('#wrapper'),
                intro: 'Esta es la lista de insumos que hay en el sistema',

            },
            {
                element: document.querySelector('#btn-agregar-insumo'),
                intro: 'Este es el botón para agregar un insumo',

            },
            {
                element: document.querySelector('[data-column-id="acciones"]'),
                intro: 'Acá puedes ver las acciones que puedes realizar con cada insumo, como editar o actualizar el stock',
            },
            

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}

function tutorial_archivo() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('#archivos'),
                intro: 'Esta es la lista de archivos que has subido al sistema y los que te han compartido',

            },
            {
                element: document.querySelector('#dropzone'),
                intro: 'Este es el espacio para subir archivos, puedes arrastrar los archivos que quieras subir, o hacer click para seleccionarlos',

            },
            {
                element: document.querySelector('[data-column-id="nombre"]'),
                intro: 'Al presionar el nombre de un archivo, este se descargará',
            },            
            {
                element: document.querySelector('[data-column-id="acciones"]'),
                intro: 'Acá puedes ver las acciones que puedes realizar con cada archivo, como compartir o eliminar',
            },
            

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}

function tutorial_perfil_usuario() {
    introJs().setOptions({
        steps: [
            {
                element: document.querySelector('#info-usuario'),
                intro: 'Aquí puedes ver los datos del usuario.',

            },
            {
                element: document.querySelector('#seleccion-imagen'),
                intro: 'Aqui puedes seleccionar una imagen de perfil.',

            },
            {
                element: document.querySelector('#btn-cambiar-contraseña'),
                intro: 'Acá puedes cambiar la contraseña del usuario.',
            }

        ],
        nextLabel: 'Siguiente',
        prevLabel: 'Anterior',
        skipLabel: 'X',
        doneLabel: 'Salir',
    }).start();
}