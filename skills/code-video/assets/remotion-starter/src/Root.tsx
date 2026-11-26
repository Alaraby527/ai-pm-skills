import { Composition } from "remotion";
import { Main } from "./Main";
import { film } from "./theme";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={film.durationInFrames}
    fps={film.fps}
    width={film.width}
    height={film.height}
  />
);
