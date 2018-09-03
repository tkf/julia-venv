Base.include(Main, joinpath(@__DIR__, "startup.jl"))

# From Base._start:
@eval Main import Base.MainInclude: eval, include
try
    Base.exec_options(Base.JLOptions())
catch err
    Base.invokelatest(Base.display_error, err, catch_backtrace())
    exit(1)
end
if Base.is_interactive && Base.have_color
    print(Base.color_normal)
end
