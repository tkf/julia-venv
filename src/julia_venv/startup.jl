if !any(isequal(@__DIR__), Base.LOAD_PATH)
    pushfirst!(Base.LOAD_PATH, @__DIR__)
end
using JuliaVenv
