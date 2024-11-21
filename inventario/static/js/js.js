$(document).ready(function () {
$(".select2").select2();
});
//esto es para que funcionen todos los select2
$('#add-department-icon').on('click', function(event) {
    event.preventDefault();  // Previene el comportamiento por defecto del enlace
$('#nuevo-departamento-field').toggle();

});
$('#add-person-icon').on('click', function(event) {
      event.preventDefault();  // Previene el comportamiento por defecto del enlace
    $('#nueva-persona-field').toggle();
});



document.addEventListener('DOMContentLoaded', function () {
    const ths = document.querySelectorAll('.sortable');

    ths.forEach(th => {
        th.addEventListener('click', function () {
            // Eliminar clases de todos los ths excepto el actual
            ths.forEach(th => {
                if (th !== this) {
                    th.classList.remove('ascendente', 'descendente');
                }
            });

            // Alternar entre ascendente, descendente, y sin orden
            if (this.classList.contains('ascendente')) {
                this.classList.remove('ascendente');
                this.classList.add('descendente');
            } else if (this.classList.contains('descendente')) {
                this.classList.remove('descendente');
                this.classList.remove('ascendente');
            } else {
                this.classList.add('ascendente');
            }

            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const index = Array.from(this.parentElement.children).indexOf(this);
            const rows = Array.from(tbody.querySelectorAll('tr'));

            // Determinar el tipo de ordenamiento basado en la clase
            let isAscending = this.classList.contains('ascendente');
            let isDescending = this.classList.contains('descendente');

            // Si ninguna clase está presente, volver al orden original
            if (!isAscending && !isDescending) {
                return;
            }

             // Ordenar las filas basado en el contenido de la columna
            rows.sort((rowA, rowB) => {
                const cellA = rowA.querySelectorAll('td')[index].textContent.trim();
                const cellB = rowB.querySelectorAll('td')[index].textContent.trim();
                
                // Detectar si el contenido es un número
                const numA = parseFloat(cellA.replace(/,/g, ''));
                const numB = parseFloat(cellB.replace(/,/g, ''));
                const isNumeric = !isNaN(numA) && !isNaN(numB);

                // Detectar si el contenido es una fecha
                const dateA = new Date(cellA);
                const dateB = new Date(cellB);
                const isDate = !isNaN(dateA) && !isNaN(dateB);

                if (isNumeric) {
                    return isAscending ? numA - numB : numB - numA;
                } else if (isDate) {
                    return isAscending ? dateA - dateB : dateB - dateA;
                } else {
                    return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
                }
            });

            // Agregar filas ordenadas de nuevo al tbody
            rows.forEach(row => tbody.appendChild(row));
        });
    });
});
