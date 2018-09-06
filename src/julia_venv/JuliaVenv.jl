__precompile__(false)
module JuliaVenv

using Pkg

const venv_depot = joinpath(@__DIR__, "depot")

const orig_DEPOT_PATH = Ref{Vector{String}}()
const orig_exename = Ref{String}()
const orig_bindir = Ref{String}()

const current_exename = Ref{String}()

function __init__()
    ### Set `DEPOT_PATH[1] = HERE/depot`
    orig_DEPOT_PATH[] = copy(Base.DEPOT_PATH)

    # Default `Base.DEPOT_PATH[1] = "~/.julia"` (`Base.init_depot_path`)
    default_depot1 = joinpath(homedir(), ".julia")

    # `DEPOT_PATH` without "~/.julia":
    depots = filter(!isequal(default_depot1), Base.DEPOT_PATH)
    # TODO: Maybe add an option to "overlay" venv depot on top of the
    #       standard depot including ~/.julia?
    # TODO: Handle `haskey(ENV, "JULIA_DEPOT_PATH")`?

    if isempty(depots) || depots[1] != venv_depot
        pushfirst!(depots, venv_depot)
    end
    append!(empty!(Base.DEPOT_PATH), depots)

    ### Prepare for `monkey_patching_julia_cmd`:
    orig_bindir[] = Sys.BINDIR
    orig_exename[] = Base.julia_exename()
    current_exename[] = orig_exename[]

    @eval JuliaVenv Base.julia_exename() = current_exename[]
end

"""
    monkey_patching_julia_cmd(f)

Do `f` while `Base.julia_cmd` is patched to return the command using
`julia-venv`.
"""
function monkey_patching_julia_cmd(f)
    try
        current_exename[] = "julia-venv"
        @eval Sys BINDIR = $(dirname(ENV["JULIA_VENV_PYTHON"]))

        @info "Monkey patched julia_cmd() = $(Base.julia_cmd())"
        return f()
    finally
        current_exename[] = orig_exename[]
        @eval Sys BINDIR = $(orig_bindir[])
    end
end

"""
    precompile_package(pkg::Union{String, Vector{String}})
    precompile_package(packages::AbstractVector{Union{AbstractString, Symbol}})

Precompile package(s) using `julia-venv`.
"""
precompile_package(package::AbstractString) = precompile_package([package])

function precompile_package(packages::AbstractVector{<: AbstractString})
    pkgids = Base.identify_package.(packages)
    not_found = findall(isequal(nothing), pkgids)
    if !isempty(not_found)
        error("Package(s) not fond: $(packages[not_found])")
    end
    monkey_patching_julia_cmd() do
        for id in pkgids
            Base.compilecache(id)
        end
    end
end

"""
    add(pkg::Union{String, Vector{String}})
    add(pkg::Union{PackageSpec, Vector{PackageSpec}})

Like `Pkg.add` but precompile packages using `precompile_package`, so
that it's safe to import them afterward in `julia-venv`.
"""
add(package::AbstractString) = add([package])
add(packages::AbstractVector{<: AbstractString}) = add(PackageSpec.(packages))
add(package::PackageSpec) = add([package])

function add(packages::AbstractVector{PackageSpec})
    Pkg.add(copy(packages))  # Pkg.add mutates `packages`
    precompile_package([p.name for p in packages])
end

end  # module
