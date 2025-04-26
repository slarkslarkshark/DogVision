document.addEventListener('DOMContentLoaded', () => {
    const buttons = {
        up: document.getElementById('up'),
        down: document.getElementById('down'),
        left: document.getElementById('left'),
        right: document.getElementById('right'),
        reset: document.getElementById('reset'),
    };

    // Функция для отправки команды на сервер
    function sendCommand(direction) {
        fetch('/camera/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ direction }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    // Обработчики событий для кнопок
    buttons.up.addEventListener('click', () => sendCommand('up'));
    buttons.down.addEventListener('click', () => sendCommand('down'));
    buttons.left.addEventListener('click', () => sendCommand('left'));
    buttons.right.addEventListener('click', () => sendCommand('right'));

    // Обработчик для кнопки Reset
    buttons.reset.addEventListener('click', () => {
        fetch('/camera/reset', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
