using JSON
using SparseArrays

function cria_bloco(delta_x, delta_y)
    bloco = zeros(Float64, 5, 1)
    bloco[2] = -1
    bloco[3] = -1
    bloco[1] = 2 * ((delta_x / delta_y)^2 + 1)
    bloco[4] = -(delta_x / delta_y)^2
    bloco[5] = bloco[4]
    return bloco
end

function assembly(connect, condicoes_contorno, bloco)
    quantidade_pontos = size(connect, 1)
    A = spzeros(Float64, quantidade_pontos, quantidade_pontos)
    b = zeros(Float64, quantidade_pontos, 1)
    
    for i = 1:quantidade_pontos
        A[i,i] = bloco[1]
        for j = 1:4
            col = connect[i][j]
            if col != 0
                if condicoes_contorno[col][1] == 0
                    A[i,col] = bloco[j + 1]
                else
                    b[i,1] -= bloco[j + 1] * condicoes_contorno[col][2]
                end
            end
        end
    end
    return A, b
end


function main()
    # Variáveis do problema
    entradas = JSON.parsefile("problema.json")
    condicoes_contorno = entradas["temperaturas"]
    connect = entradas["connect"]
    step_x = entradas["step"]["step_x"]
    step_y = entradas["step"]["step_y"]
    bloco = cria_bloco(step_x, step_y)
    display(bloco)
    A, b = assembly(connect, condicoes_contorno, bloco)
    n = size(connect, 1)
    for i = 1:n
        if condicoes_contorno[i][1] == 1
            A[i,:] = zeros(Float64, 1, n)
            A[i,i] = 1
            b[i,1] = condicoes_contorno[i][2]
        end
    end
    x = A \ b

    f = open("resultado.json", "w")
    JSON.print(f, x, 4) 
    close(f)  # or flush(f)
end

main()

