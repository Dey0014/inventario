//esto es para que funcionen todos los select2
$(document).ready(function () {
$(".select2").select2({
    width: '100%',
    placeholder: "",
    allowClear: true
});
});
$(document).ready(function () {
    $(".matselec").select2({
        width: '100%',
        placeholder: "Selecciona una Material",
        allowClear: true
    });
});

$(document).ready(function () {
    $(".herselec").select2({
        width: '100%',
        placeholder: "Selecciona una Herramienta",
        allowClear: true
    });
});


$(document).ready(function () {
    $(".selectDepartment").select2({
        width: '100%',
        placeholder: "Selecciona un Departamento",
        allowClear: true
    });
});


$(document).ready(function () {
    $(".per").select2({
        width: '100%',
        placeholder: "Selecciona una Persona",
        allowClear: true
    });
});

// ------------------------------------------
$(document).ready(function() {
    let personaSelect = $('#persona');  // Select2 de personas
    let departamentoSelect = $('#departamento'); // Select2 de departamentos
    
    let personaSeleccionada = null;
    let departamentoSeleccionado = null;



    // Evento para mostrar el formulario de nueva persona
    $('#showNewPeople').on('click', function() {
        personaSeleccionada = personaSelect.val();  // Guardar selección actual
        personaSelect.val('').trigger('change'); // Limpiar Select2

        $('#inputPeople').hide();
        $('#newPeopleForm').show();
    });

    // Evento para cerrar el formulario de nueva persona
    $('#closeNewPeople').on('click', function() {
        $('#newPeopleForm').hide();
        $('#inputPeople').show();

        // Restaurar la selección previa si existía
        if (personaSeleccionada) {
            personaSelect.val(personaSeleccionada).trigger('change');
        }
    });

    // Evento para mostrar el formulario de nuevo departamento
    $('#showNewDepartment').on('click', function() {
        departamentoSeleccionado = departamentoSelect.val();
        departamentoSelect.val('').trigger('change');

        $('#inputDepartment').hide();
        $('#newDepartmentForm').show();
    });

    // Evento para cerrar el formulario de nuevo departamento
    $('#closeNewDepartment').on('click', function() {
        $('#newDepartmentForm').hide();
        $('#inputDepartment').show();

        if (departamentoSeleccionado) {
            departamentoSelect.val(departamentoSeleccionado).trigger('change');
        }
    });
});
// ------------------------------------------

// muestra el content si tiene algun contenido 
document.addEventListener("DOMContentLoaded", function () {
    var contenidoDiv = document.getElementById("ver");
    if (contenidoDiv.innerHTML.trim() === "") {
    contenidoDiv.classList.add("hidden");
    }
});
// ------------------------------------------

// evita que muestren respuestas automaticas guardadas en cache 
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("input").forEach(input => {
        input.setAttribute("autocomplete", "off");
    });
});
//-------------------------------------------
//funcion para data table

$(document).ready(function() {
    // Inicializar DataTables en todas las tablas con la clase "tablasApp"
    $('.tablasApp').each(function(index) {
        var tabla = $(this).DataTable({
            "paging": true,         // Permite la paginación
            "ordering": false,       // Habilita la ordenación
            "info": false,          // Deshabilita la información
            "searching": true,  // Habilitamos la búsqueda interna
            "lengthChange": false,  // Deshabilita la opción de cambiar el número de registros por página
            "pageLength": 10,       // Muestra 10 registros por página
            "language": {
                "paginate": {
                    "first": "Primero",
                    "last": "Último",
                    "next": "▶",
                    "previous": "◀"
                },
                "zeroRecords": "No se encontraron resultados"
            },
            "initComplete": function(settings, json) {
                $(".dt-search").hide();  // Ocultamos el filtro de búsqueda interno
            },
            
        });

        // Seleccionamos el campo de búsqueda externo con el ID generado dinámicamente
        $('.searchInput').on('keyup', function() {
            tabla.search($(this).val()).draw();  // Filtra los resultados de la tabla basado en el valor del input
        });
    });

    // Evento para limpiar los buscadores cuando se cambia de tab
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function() {
        $('.searchInput').val(''); // Borra el contenido de todos los buscadores
        $('.tablasApp').each(function() {
            $(this).DataTable().search('').draw(); // Restablece la búsqueda de todas las tablas
        });
    });
});
//-------------------------------------------
//----------------funcion para pasar los datos de materiales al pdf



$('#printmateriales').click(async function () {
    const table = $('.tablasApp:visible').DataTable();
    const usuario = $('#nombreUsuarioActivo').text() || 'Desconocido';
    const fecha = new Date().toLocaleString('es-VE');
    let titulotabla = $('.tablasApp:visible').attr('data-name') || 'Tabla Desconocida';

    const materiales = [];
    table.rows({ search: 'applied' }).every(function () {
        let data = this.data();
        materiales.push({
            codigo: data[0],
            descripcion: data[1],
            tipo: data[5],
            coordinador: data[3],
            fecha_ingreso: data[4],
            cantidad: data[2],
        });
    });

    const res = await fetch('../materiales/pdf_materiales/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': "{{ csrf_token }}"  // si usas CSRF
        },
        body: JSON.stringify({
            materiales: materiales,
            usuario: usuario,
            fecha: fecha,
            titulo: titulotabla
        })
    });

    // Abrir el PDF en una nueva pestaña
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
});

    document.getElementById("togglePassword").addEventListener("click", function () {
        var passwordField = document.getElementById("id_password");
        var icon = this.querySelector("i");

        if (passwordField.type === "password") {
            passwordField.type = "text";
            icon.classList.remove("bi-eye");
            icon.classList.add("bi-eye-slash");
        } else {
            passwordField.type = "password";
            icon.classList.remove("bi-eye-slash");
            icon.classList.add("bi-eye");
        }
    });

//----------------------------------------------------
