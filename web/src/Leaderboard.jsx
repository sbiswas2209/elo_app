import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import {
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Button,
} from "@mui/material";
import { ArrowUpward, ArrowDownward, Remove } from "@mui/icons-material";

const API_URL = "http://localhost:8000/api/recommend/leaderboard"; // Replace with your FastAPI URL

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLeaderboard = useCallback(async () => {
    setLoading(true);
    axios
      .get(API_URL)
      .then((response) => {
        setLeaderboard(response.data);
      })
      .catch((error) => {
        console.error("Error fetching leaderboard:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  return (
    <Container>
      <Button href="/">Home Page</Button>
      <Typography variant="h4" align="center" sx={{ my: 3 }}>
        Leaderboard
      </Typography>
      {loading ? (
        <CircularProgress sx={{ display: "block", margin: "auto" }} />
      ) : (
        <TableContainer
          component={Paper}
          sx={{ maxWidth: 600, margin: "auto" }}
        >
          <Table>
            <TableHead>
              <TableRow>
                <TableCell align="center">
                  <b>Rank</b>
                </TableCell>
                <TableCell>
                  <b>Name</b>
                </TableCell>
                <TableCell align="center">
                  <b>Rating</b>
                </TableCell>
                <TableCell align="center">
                  <b>Change</b>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leaderboard.map((actress, index) => (
                <TableRow key={actress.rank}>
                  <TableCell align="center">{index + 1}</TableCell>
                  <TableCell>{actress.name}</TableCell>
                  <TableCell align="center">{actress.rating}</TableCell>
                  <TableCell align="center">
                    {actress.previous_rank > actress.rank ? (
                      <ArrowUpward color="success" />
                    ) : actress.previous_rank < actress.rank ? (
                      <ArrowDownward color="error" />
                    ) : (
                      <Remove />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default Leaderboard;
