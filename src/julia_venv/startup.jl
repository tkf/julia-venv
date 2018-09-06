# Do monkey patches (via JuliaVenv) only in the "root" julia-venv
# process. `Base.compilecache` uses `Base.load_path_setup_code` to
# propagate so there is no need to setup `Base.DEPOT_PATH` manually
# inside child processes launched by `Base.compilecache`.
if get(ENV, "_JULIA_VENV_PROCESS", "") != "true"
    if !any(isequal(@__DIR__), Base.LOAD_PATH)
        pushfirst!(Base.LOAD_PATH, @__DIR__)
    end
    @eval using JuliaVenv
end
ENV["_JULIA_VENV_PROCESS"] = "true"
