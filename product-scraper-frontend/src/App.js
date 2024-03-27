import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Import CSS file for styles

const App = () => {
  const [products, setProducts] = useState([]);
  const [pageSize, setPageSize] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getProducts(); 
  }, []); 

  const getProducts = async () => {
    try {
      setLoading(true);
      const token = 'test_static_token';
      const headers = { headers: { Authorization: token } };

      const response = await axios.get(`http://localhost:8000/pages/${pageSize}`, headers);
      setProducts(response.data.result);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching products:', error);
      window.alert('Error in fetching products details');
    }
  };

  const handlePageSizeChange = (event) => {
    setPageSize(event.target.value);
  };

  const getTotalProductsInfo = () => {
    const totalCount = products.length;
    const totalPrices = products.reduce((acc, curr) => acc + parseFloat(curr.product_price), 0);
    return { totalCount, totalPrices };
  };

  const { totalCount, totalPrices } = getTotalProductsInfo();

  return (
    <div className="App">
      <h3>Scraping from - <a href='https://dentalstall.com/shop/' target='_blank' rel='noopener noreferrer'>https://dentalstall.com/shop/</a></h3>
      <h1 className="title">Product Scraper</h1>
      <div className="center-content">
        <label htmlFor="pageSize">Page Size:</label>
        <input
          type="number"
          id="pageSize"
          name="pageSize"
          min="1"
          value={pageSize}
          onChange={handlePageSizeChange}
        />
        {!loading && <button className="get-products-btn" onClick={getProducts}>Get Products</button>}
        {loading && <h3>Loading.....</h3>}
      </div>
      <div className="product-list center-content">
        {products.length > 0 && (
          <>
            <div className="total-info">
              <p>Total Products: {totalCount}</p>
              <p>Total Price: ₹{totalPrices.toFixed(2)}</p>
            </div>
            <table className="product-table">
              <thead>
                <tr>
                  <th>Serial No</th>
                  <th>Product Id</th>
                  <th>Product Title</th>
                  <th>Product Price</th>
                  <th>Product Image</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product, index) => (
                  <tr key={product.product_id}>
                    <td>{index + 1}</td>
                    <td>{product.product_id}</td>
                    <td>{product.product_title}</td>
                    <td>₹{product.product_price}</td>
                    <td>
                      <a href={product.path_to_image} target="_blank" rel="noopener noreferrer">
                        View Image
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  );
};

export default App;
