// Подключаем и инициализируем график только после загрузки DOM
document.addEventListener("DOMContentLoaded", function () {
    // Инициализация графика
    const ctx = document.getElementById('earningsChart').getContext('2d');

    // Убедимся, что элемент существует
    if (!ctx) {
        console.error("Canvas element not found!");
        return;
    }

    let earningsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Прибыль', 'Выплаты', 'Маркетинговые инструменты', 'Инвестиционная аналитика'],
            datasets: [{
                label: 'Значения',
                data: [5929, 100, 10, 80], // начальные данные
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)', // зеленый
                    'rgba(255, 99, 132, 0.2)', // красный
                    'rgba(255, 159, 64, 0.2)', // оранжевый
                    'rgba(54, 162, 235, 0.2)'  // синий
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Обработчик для кнопки "Сохранить"
    document.getElementById('saveData').addEventListener('click', function () {
        // Получаем значения из полей ввода
        const profit = parseInt(document.getElementById('profit').value);
        const payout = parseInt(document.getElementById('payout').value);
        const referral = parseInt(document.getElementById('referral').value);
        const conversion = parseInt(document.getElementById('conversion').value);

        // Проверяем, что данные валидны
        if (!isNaN(profit) && !isNaN(payout) && !isNaN(referral) && !isNaN(conversion)) {
            // Обновляем данные графика
            earningsChart.data.datasets[0].data = [profit, payout, referral, conversion];

            // Перерисовываем график
            earningsChart.update();
        } else {
            alert("Пожалуйста, введите валидные числа для всех полей.");
        }
    });
});

const applicationsMenuItem = document.getElementById("applications");
const popupWindow = document.getElementById("popup-window");

// Показывать окно при наведении
applicationsMenuItem.addEventListener("mouseenter", () => {
    popupWindow.classList.remove("hidden");
    popupWindow.classList.add("visible");
});

// Скрывать окно, когда мышь уходит
applicationsMenuItem.addEventListener("mouseleave", () => {
    popupWindow.classList.remove("visible");
    popupWindow.classList.add("hidden");
});