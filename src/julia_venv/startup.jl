if ! @isdefined __py_julia_venv_orig_DEPOT_PATH
    __py_julia_venv_orig_DEPOT_PATH = copy(Base.DEPOT_PATH)
end

let venv_depot = joinpath(@__DIR__, "depot")

    # Default `Base.DEPOT_PATH[1] = "~/.julia"` (`Base.init_depot_path`)
    default_depot1 = joinpath(homedir(), ".julia")

    # `DEPOT_PATH` without "~/.julia":
    depots = filter(!isequal(default_depot1), __py_julia_venv_orig_DEPOT_PATH)
    # TODO: Maybe add an option to "overlay" venv depot on top of the
    #       standard depot including ~/.julia?
    # TODO: Handle `haskey(ENV, "JULIA_DEPOT_PATH")`?

    if isempty(depots) || depots[1] != venv_depot
        pushfirst!(depots, venv_depot)
    end
    append!(empty!(Base.DEPOT_PATH), depots)
end
