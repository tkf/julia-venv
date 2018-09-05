Base.include(Main, joinpath(@__DIR__, "startup.jl"))

command_list = copy(ARGS)
if isempty(command_list)
    command_list = ["add"]
end
for (i, command) in enumerate(command_list)
    if command ∉ ["add", "build", "compile"]
        error("Unknown $i-th command: $command")
    end
end

@info """
Base.DEPOT_PATH is initialized to:
$(sprint(show, "text/plain", Base.DEPOT_PATH))
"""

ENV["PYTHON"] = ENV["JULIA_VENV_PYTHON"]
import Pkg

let venv_depot = joinpath(@__DIR__, "depot")
    for command in command_list
        if command == "add"
            if "PyCall" ∉ keys(Pkg.installed())
                @info "Installing PyCall.jl..."
                @assert Base.DEPOT_PATH[1] == venv_depot
                Pkg.add("PyCall")
            else
                @info "PyCall.jl is already installed"
            end
        elseif command == "build"
            Pkg.build("PyCall")
        elseif command == "compile"
            # Manually removing PyCall's precmopile file since it may
            # not be detected as "stale" by julia when it was compiled
            # in non-PyJulia -mode.
            pkg = Base.identify_package("PyCall")
            if pkg !== nothing
                cache_files = Base.find_all_in_cache_path(pkg)
                if !isempty(cache_files) &&
                        startswith(cache_files[1], venv_depot)
                    @info """
                    Removing old compilation cache for PyCall:
                    $(cache_files[1])
                    """
                    rm(cache_files[1], force = true)
                end
            end
            @info "Compiling PyCall..."
            @eval Main import PyCall
        else
            error("Unknown command $command")
        end
    end
end
