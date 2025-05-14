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

//funcion para imprimir las herramientas

$('#printBtn').click(function() {
    var tableData = [];
    var table = $('.tablasApp').DataTable();
    table.rows({ search: 'applied' }).every(function() {
        var rowData = this.data();
        
        // Omitir la última columna (acción)
        rowData = rowData.slice(0, -1); // Elimina la última columna de cada fila
        
        // Asegúrate de que cada celda tenga un valor válido (puedes reemplazar undefined por '-')
        rowData = rowData.map(cell => cell !== undefined ? cell : '-');
        
        tableData.push(rowData);
    });

    console.log(tableData); // Comprobar los datos antes de pasarlos al PDF

    var docDefinition = {
        content: [
            { text: 'Contenido de la Tabla', style: 'header' },
            {
                table: {
                    headerRows: 1,
                    body: [
                        ['#', 'Descripción', 'Cantidad', 'Coordinador', 'Fecha de Ingreso', 'Condición'], // Sin la columna de acciones
                        ...tableData
                    ]
                },
                layout: 'lightHorizontalLines'
            }
        ],
        styles: {
            header: {
                fontSize: 18,
                bold: true,
                alignment: 'center',
                margin: [0, 20, 0, 20]
            }
        }
    };

    pdfMake.createPdf(docDefinition).download('tabla.pdf');
});


//-------------------------------------

$('#pruebasss').click(async function() {
    try {
        var logoBase64 = await obtenerBase64FromImage('/static/img/logo.png'); // Esperar a que la imagen se convierta


        var tableData = [];
        var table = $('.tablasApp:visible').DataTable();

        // Obtener el nombre de la tabla
        var tableName = $('.tablasApp:visible').attr('data-name') || 'Tabla Desconocida';

        table.rows({ search: 'applied' }).every(function() {
            var rowData = this.data();
            rowData = rowData.slice(0, -1); // Elimina la última columna
            rowData = rowData.map(cell => cell !== undefined ? cell : '-');
            tableData.push(rowData);
        });

        console.log(tableData); // Verifica los datos antes de generar el PDF

        var docDefinition = {
            pageSize: 'A4', // Tamaño de la página
            pageOrientation: 'landscape',
            pageMargins: [40, 60, 40, 60], // Márgenes
            content: [
                {
                    table: {
                        headerRows: 1,
                        widths: ['10%', '30%', '10%', '20%', '20%', '10%'], // Hace que la tabla ocupe el 100%
                        body: [
                            ['Código', 'Descripción', 'Cantidad', 'Coordinador', 'Fecha de Ingreso', 'Tipo'],
                            ...tableData
                        ],
                        dontBreakRows: true, // Evita que las filas se dividan en páginas
                    },
                    layout: 'lightHorizontalLines'
                }
            ],
            header: function(currentPage, pageCount, pageSize) {
                return {
                    columns: [
                        {
                            image: logoBase64, // Logo a la izquierda
                            width: 80,
                            alignment: 'left',
                            margin: [10, 10]
                        },
                        {   
                            text: tableName, // Nombre centrado correctamente
                            alignment: 'center',
                            fontSize: 22,
                            bold: true,
                            margin: [10, 10],
                            width: '*'
                        },
                        {
                            text: 'Usuario', // Usuario alineado a la derecha
                            alignment: 'right',
                            fontSize: 8,
                            margin: [10, 10],
                            width: 80
                        }
                    ],
                    columnGap: 8, // Espaciado entre columnas
                };
            },
            footer: function(currentPage, pageCount) {
                return {
                    text: `Página ${currentPage} de ${pageCount}\nCentro Nacional de Acción Social por la Música, Boulevard Amador Bendayán, Caracas 1050, Distrito Capital.\n© 2024 Copyright ELSISTEMA elsistema.org.ve`,
                    alignment: 'center',
                    fontSize: 8,
                    margin: [15,10]
                };
            },
            styles: {
                header: {
                    fontSize: 18,
                    bold: true,
                    alignment: 'center',
                    margin: [0, 20, 0, 20]
                }
            }
        };

        // Generar y descargar el PDF
        pdfMake.createPdf(docDefinition).download('tabla.pdf');
    } catch (error) {
        console.error("Error al cargar la imagen:", error);
    }
});

function obtenerBase64FromImage(url) {
    return new Promise((resolve, reject) => {
        var img = new Image();
        img.crossOrigin = "Anonymous"; // Evita problemas de CORS si la imagen está en otro dominio
        img.onload = function() {
            var canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            var dataURL = canvas.toDataURL('image/png');
            resolve(dataURL);
        };
        img.onerror = function(error) {
            reject(error);
        };
        img.src = url;
    });
}

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
