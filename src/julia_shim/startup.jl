let venv_depot = joinpath(@__DIR__, "depot")
    if isempty(Base.DEPOT_PATH) || Base.DEPOT_PATH[1] != venv_depot
        pushfirst!(Base.DEPOT_PATH, venv_depot)
    end
end
