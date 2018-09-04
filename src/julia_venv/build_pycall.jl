Base.include(Main, joinpath(@__DIR__, "startup.jl"))

let venv_depot = joinpath(@__DIR__, "depot")
    pkg = Base.identify_package("PyCall")
    cache_files = Base.find_all_in_cache_path(pkg)
    if isempty(cache_files) || !startswith(cache_files[1], venv_depot)
        @eval Main begin
            import Pkg
            ENV["PYTHON"] = ENV["JULIA_VENV_PYTHON"]
            Pkg.build("PyCall")
            import PyCall
        end
    end
end
