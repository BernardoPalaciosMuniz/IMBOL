makeoutput(Dd,U,D,t,filename)
function makeoutput(Dd,U,D,t,filename)
    rho=1400;
    sigma=12.4e-3;
    
    name=split(filename,'/');
    folder=name(end-2);
    name=name(end-1);
    

    if ~exist(folder, 'dir')
       mkdir(folder)
    end
    
    We=rho*U^2*Dd/sigma;
    Dmax=max(D);
    T = array2table([Dd,U,We,Dmax]);
    T.Properties.VariableNames(1:4) = {'D_d [m]','U_d [m/s]','We','D_max'};
    writetable(T,folder+'/'+name+'_We_Rmax.csv','Delimiter',',');
    
    T = array2table([t,D]);
    T.Properties.VariableNames(1:2) = {'t [s]','D [m]'};
    writetable(T,folder+'/'+name+'_Rvst.csv','Delimiter',',');
    

end