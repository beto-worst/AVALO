//Funcionalidad de legal
function legal() {
    const legalScore = document.querySelector('.legal-score')
    if(legalScore.innerHTML) {
        legalScore.parentNode.classList.remove("correct")
        legalScore.parentNode.classList.add("bad")
    }
    else {
        legalScore.parentNode.classList.remove("bad")
        legalScore.parentNode.classList.add("correct")
    }
}
legal()

//Funcionalidad de internacional
function internacional() {
    const internationalScore = document.querySelector('.international-score')
    if(internationalScore.innerHTML) {
        internationalScore.parentNode.classList.remove("correct")
        internationalScore.parentNode.classList.add("bad")
    }
    else {
        internationalScore.parentNode.classList.remove("bad")
        internationalScore.parentNode.classList.add("correct")
    }
}
internacional()

//Funcionalidad de tacómetro
function tacometro() {
    const flechaTacometro = document.querySelector('.tachometer-indicator')
    const valor = Number(document.querySelector('.score-value').innerHTML)

    if(valor <= 550) {
        flechaTacometro.style.transform = "rotate(-72deg)"
        flechaTacometro.parentNode.parentNode.classList.remove('regular')
        flechaTacometro.parentNode.parentNode.classList.remove('good')
        flechaTacometro.parentNode.parentNode.classList.remove('excellent')
        flechaTacometro.parentNode.parentNode.classList.add('bad')
    }
    else if(valor >= 551 && valor <= 630) {
        flechaTacometro.style.transform = "rotate(-36deg)"
        flechaTacometro.parentNode.parentNode.classList.remove('bad')
        flechaTacometro.parentNode.parentNode.classList.remove('good')
        flechaTacometro.parentNode.parentNode.classList.remove('excellent')
        flechaTacometro.parentNode.parentNode.classList.add('regular')
    }
    else if(valor >= 631 && valor <= 680) {
        flechaTacometro.style.transform = "rotate(36deg)"
        flechaTacometro.parentNode.parentNode.classList.remove('bad')
        flechaTacometro.parentNode.parentNode.classList.remove('regular')
        flechaTacometro.parentNode.parentNode.classList.remove('excellent')
        flechaTacometro.parentNode.parentNode.classList.add('good')
    }
    else if(valor >= 681) {
        flechaTacometro.style.transform = "rotate(72deg)"
        flechaTacometro.parentNode.parentNode.classList.remove('bad')
        flechaTacometro.parentNode.parentNode.classList.remove('regular')
        flechaTacometro.parentNode.parentNode.classList.remove('good')
        flechaTacometro.parentNode.parentNode.classList.add('excellent')
    }
}
tacometro()

//Funcionalidad de academico
function academico() {
    const academicScore = document.querySelector('.academic-score')
    if(academicScore.innerHTML == "N/A") {
        academicScore.parentNode.classList.add('none')
    }
    else {
        academicScore.parentNode.classList.remove('none')
    }
}
academico()

//Setters para valores de evaluación
function setLegalScore(score) {
    //Score debe ser un string que represente el valor de la categoría (ejemplo: "5"). Si no hay ningún expediente, pasar un string vacío ""
    document.querySelector('.legal-score').innerHTML = score
    legal()
}
function setInternationalScore(score) {
    //Score debe ser un string que represente el valor de la categoría (ejemplo: "5"). Si no hay ningún expediente, pasar un string vacío ""
    document.querySelector('.international-score').innerHTML = score
    internacional()
}
function setScoreValue(value) {
    //Value debe ser un string con un número del 456 al 760
    document.querySelector('.score-value').innerHTML = value
    tacometro()
}
function setAcademicScore(score) {
    //score debe ser un string con el número de expedientes académicos encontrados. Si no hay ninguno, pasar un string así: "N/A"
    document.querySelector('.academic-score').innerHTML = score
    academico()
}