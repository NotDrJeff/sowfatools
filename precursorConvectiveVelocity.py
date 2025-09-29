import numpy as np

def main():
    resolved_vertical_flux = np.loadtxt('p001_Tw_mean_16000_20000.gz')
    sgs_vertical_flux = np.loadtxt('p001_q3_mean_16000_20000.gz')

    total_vertical_flux = resolved_vertical_flux
    total_vertical_flux[:,1] += sgs_vertical_flux[:,1]
    del resolved_vertical_flux, sgs_vertical_flux

    zi = total_vertical_flux[np.argmin(total_vertical_flux[:,1]),0]
    w_star = ( 9.81/300 * 0.04 * zi )**(1/3)

    print(f'{zi=}')
    print(f'{w_star=}')


if __name__ == '__main__':
    main()

