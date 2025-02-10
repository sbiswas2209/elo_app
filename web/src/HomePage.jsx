import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import {
  CircularProgress,
  Grid,
  Card,
  CardMedia,
  Snackbar,
  Typography,
  Button,
  Container,
} from "@mui/material";

const API_BASE_URL = "https://eloapp-production.up.railway.app/api/recommend";

const HomePage = () => {
  const [actresses, setActresses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userId] = useState(uuidv4());

  const fetchActresses = useCallback(
    async (winnerId = null, loserId = null) => {
      setIsLoading(true);
      try {
        const response = await axios.post(
          `${API_BASE_URL}/fetch`,
          {
            actress_one_id: winnerId,
            actress_two_id: loserId,
          },
          {
            headers: { "Content-Type": "application/json", "user-id": userId },
          }
        );

        if (!response.data.actress_1 || !response.data.actress_2) {
          setActresses([]);
        } else {
          setActresses([response.data.actress_1, response.data.actress_2]);
        }
      } catch (error) {
        console.log(error);
        setError("Failed to load actresses");
      } finally {
        setIsLoading(false);
      }
    },
    [userId]
  );

  useEffect(() => {
    fetchActresses();
  }, [fetchActresses]);

  const submitChoice = async (winnerId, loserId) => {
    setIsLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/score`, {
        winner_id: winnerId,
        loser_id: loserId,
      });
      await fetchActresses(winnerId, loserId);
    } catch (error) {
      console.log(error);
      setError("Failed to submit choice");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <CircularProgress />;

  return (
    <Container>
      <Button href="/leaderboard">Leaderboard</Button>
      {actresses.length === 0 ? (
        <Typography>No actresses available. End of list.</Typography>
      ) : (
        <Grid container spacing={2} justifyContent="center">
          {actresses.map((actress) => (
            <Grid item xs={12} md={6} key={actress._id}>
              <Card
                sx={{ cursor: "pointer" }}
                onClick={() =>
                  submitChoice(
                    actress._id,
                    actresses.find((a) => a._id !== actress._id)._id
                  )
                }
              >
                <CardMedia
                  component="img"
                  height="400"
                  image={actress.url}
                  alt="Actress"
                  onError={(e) =>
                    (e.target.src =
                      "https://via.placeholder.com/400x400?text=Image+Not+Available")
                  }
                />
              </Card>
            </Grid>
          ))}
          <Snackbar
            open={Boolean(error)}
            autoHideDuration={4000}
            message={error}
            onClose={() => setError(null)}
          />
        </Grid>
      )}
    </Container>
  );
};

export default HomePage;
