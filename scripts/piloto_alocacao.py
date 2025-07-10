import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Cuboid:
    def __init__(self, dx: float, dy: float, dz: float):
        self.dx, self.dy, self.dz = dx, dy, dz
        self.center = np.array([dx/2, dy/2, dz/2])

    def _rotation_matrix(self, roll: float, pitch: float, yaw: float) -> np.ndarray:
        r, p, y = map(math.radians, (roll, pitch, yaw))
        Rx = np.array([[1,0,0],[0,math.cos(r),-math.sin(r)],[0,math.sin(r),math.cos(r)]])
        Ry = np.array([[math.cos(p),0,math.sin(p)],[0,1,0],[-math.sin(p),0,math.cos(p)]])
        Rz = np.array([[math.cos(y),-math.sin(y),0],[math.sin(y),math.cos(y),0],[0,0,1]])
        return Rz @ Ry @ Rx

    def _get_vertices(self, origin, lx, ly, lz, R=None):
        pts = np.array([
            [0,0,0],[lx,0,0],[lx,ly,0],[0,ly,0],
            [0,0,lz],[lx,0,lz],[lx,ly,lz],[0,ly,lz]
        ]) + np.array(origin)
        if R is not None:
            pts = (pts - self.center) @ R.T + self.center
        return [tuple(p) for p in pts]

    def plot_mixed_blocks(self,
                          block_vert=(1,1,2),
                          block_horz_options=[(2,1,1), (1,2,1)],
                          rotation=(30,20,45),
                          output_path="cubo_mixed_soft.png"):
        dx, dy, dz = self.dx, self.dy, self.dz
        R = self._rotation_matrix(*rotation)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.grid(False); ax.set_axis_off()

        faces_idx = [[0,1,2,3],[4,5,6,7],[0,1,5,4],
                     [2,3,7,6],[1,2,6,5],[4,7,3,0]]

        # wireframe do cubo externo
        verts_main = self._get_vertices((0,0,0), dx, dy, dz, R=R)
        for fi in faces_idx:
            pts = [verts_main[i] for i in fi] + [verts_main[fi[0]]]
            xs, ys, zs = zip(*pts)
            ax.plot(xs, ys, zs, color='black', linewidth=1)

        # blocos verticais (1×1×2) – ciano
        lx, ly, lz = block_vert
        nz = int(dz // lz)
        for iz in range(nz):
            for iy in range(int(dy//ly)):
                for ix in range(int(dx//lx)):
                    origin = (ix*lx, iy*ly, iz*lz)
                    verts = self._get_vertices(origin, lx, ly, lz, R=R)
                    ax.add_collection3d(Poly3DCollection(
                        [[verts[i] for i in fi] for fi in faces_idx],
                        facecolor='cyan', edgecolor='blue', alpha=0.6
                    ))

        # camada horizontal restante – cor suave próxima ao ciano
        rem_h = dz - nz * lz
        best = None
        best_count = 0
        for (hx, hy, hz) in block_horz_options:
            if abs(hz - rem_h) < 1e-6:
                count = int(dx//hx) * int(dy//hy)
                if count > best_count:
                    best_count = count
                    best = (hx, hy, hz)
        if best:
            hx, hy, hz = best
            z0 = nz * lz
            for iy in range(int(dy//hy)):
                for ix in range(int(dx//hx)):
                    origin = (ix*hx, iy*hy, z0)
                    verts = self._get_vertices(origin, hx, hy, hz, R=R)
                    ax.add_collection3d(Poly3DCollection(
                        [[verts[i] for i in fi] for fi in faces_idx],
                        facecolor='#99FFFF',  # tom suave de ciano
                        edgecolor='#66CCCC',
                        alpha=0.6
                    ))

        total = nz * int(dx//lx) * int(dy//ly) + best_count
        ax.text2D(0.05, 0.95, f"Total blocks: {total}",
                  transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # limites conforme cubo rotacionado
        xs = [v[0] for v in verts_main]; ys = [v[1] for v in verts_main]; zs = [v[2] for v in verts_main]
        ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys)); ax.set_zlim(min(zs), max(zs))
        ax.set_box_aspect([1,1,1])

        fig.savefig(output_path, dpi=150)
        print(f"Figura salva em: {output_path}")
        try: plt.show()
        except: pass

if __name__ == "__main__":
    cubo = Cuboid(3, 4, 5)
    cubo.plot_mixed_blocks()
