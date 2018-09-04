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
            @eval Main import PyCall
        else
            error("Unknown command $command")
        end
    end
end
