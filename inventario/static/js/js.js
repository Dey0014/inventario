//esto es para que funcionen todos los select2
$(document).ready(function () {
$(".select2").select2({
    width: '100%',
    placeholder: "",
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

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("input").forEach(input => {
        input.setAttribute("autocomplete", "off");
    });
});

$(document).ready(function() {
    // Inicializar DataTables en todas las tablas con la clase "tablasApp"
    $('.tablasApp').each(function(index) {
        var tabla = $(this).DataTable({
            "paging": true,         // Permite la paginación
            "ordering": true,       // Habilita la ordenación
            "info": false,          // Deshabilita la información
            "searching": true,      // Habilitamos la búsqueda interna
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

function getBase64Image(url, callback) {
    var img = new Image();
    img.crossOrigin = "Anonymous"; 
    img.onload = function() {
        var canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        var dataURL = canvas.toDataURL("image/png"); // Convierte a Base64
        callback(dataURL);
    };
    img.src = url;
}

$('#pruebasss').click(function() {
    $.get('/static/img/El+sistema_cp__rgb.base64', function(base64Data) { 
        generarPDF(base64Data.trim()); // Llamar la función con la imagen Base64
    });
});

// Función para generar el PDF
function generarPDF(logoBase64) {
    var tableData = [];
    var table = $('.tablasApp').DataTable();
    var tableName = $('.tablasApp:visible').attr('data-name') || 'Tabla Desconocida';

    table.rows({ search: 'applied' }).every(function() {
        var rowData = this.data();
        rowData = rowData.slice(0, -1); // Elimina la última columna
        rowData = rowData.map(cell => cell !== undefined ? cell : '-');
        tableData.push(rowData);
    });

    var docDefinition = {
        content: [
            {
                table: {
                    headerRows: 1,
                    body: [
                        ['Código', 'Descripción', 'Cantidad', 'Coordinador', 'Fecha de Ingreso', 'Tipo'],
                        ...tableData
                    ]
                },
                layout: 'lightHorizontalLines'
            }
        ],
        pageMargins: [40, 60, 40, 60],
        header: function() {
            return {  
                columns: [
                    {
                        image: logoBase64, // Usar el contenido del archivo Base64
                        width: 100,
                        margin: [0, 10]
                    },
                    {
                        text: tableName,
                        alignment: 'center',
                        fontSize: 18,
                        margin: [0, 10]
                    }
                ]
            };
        },
        footer: function(currentPage, pageCount) {
            return {
                text: `Página ${currentPage} de ${pageCount}\nCentro Nacional de Acción Social por la Música, Boulevard Amador Bendayán, Caracas 1050, Distrito Capital.\n© 2024 Copyright ELSISTEMA elsistema.org.ve`,
                alignment: 'center',
                fontSize: 8,
                margin: [15,10]
            };
        }
    };

    pdfMake.createPdf(docDefinition).download('tabla.pdf');
}
