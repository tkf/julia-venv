Base.include(Main, joinpath(@__DIR__, "startup.jl"))

@info """
Base.DEPOT_PATH is initialized to:
$(sprint(show, "text/plain", Base.DEPOT_PATH))
"""

let venv_depot = joinpath(@__DIR__, "depot")
    pkg = Base.identify_package("PyCall")
    if pkg !== nothing
        cache_files = Base.find_all_in_cache_path(pkg)
    else
        cache_files = []
    end
    if isempty(cache_files) || !startswith(cache_files[1], venv_depot)
        @info "Installing PyCall.jl..."
        @assert Base.DEPOT_PATH[1] == venv_depot
        @eval Main begin
            import Pkg
            ENV["PYTHON"] = ENV["JULIA_VENV_PYTHON"]
            Pkg.build("PyCall")
            import PyCall
        end
    else
        @info("PyCall.jl is already compiled.",
              path = cache_files[1])
    end
end
